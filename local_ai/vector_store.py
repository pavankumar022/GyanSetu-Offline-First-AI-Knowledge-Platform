"""
vector_store.py — GyanSetu Offline Vector + Keyword Search Engine
─────────────────────────────────────────────────────────────────────────────
Changes in this version:
• Sub-topic tagging: each chunk is labelled with a sub-topic (irrigation,
  fertilizer, sowing-time, pest, disease, yield, eligibility, cost, soil,
  spacing, varieties) at index time using section-heading heuristics.
• Intent-keyword mapping: at query time a lightweight keyword→sub-topic
  lookup detects the user's intent and boosts chunks whose sub-topic matches,
  even when raw vector similarity is close across multiple chunks from the
  same document.
• Cross-crop mismatch penalty (unchanged).
"""

import os
import re
import sqlite3
import numpy as np
from typing import List, Dict, Any, Tuple
from local_ai.embeddings import get_embedding, cosine_similarity, STOPWORDS

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "device_storage")
DB_PATH = os.path.join(DB_DIR, "local_knowledge.db")

# ── Section-header detection patterns ────────────────────────────────────────
_HEADER_PATTERNS = [
    re.compile(r"^#{1,3}\s+(.+)$"),                     # markdown ## headers
    re.compile(r"^([A-Z][A-Za-z &/()—–-]{3,}):?\s*$"),  # ALL-CAPS or Title: lines
    re.compile(r"^(\d+\.\s+[A-Z].{5,}):?\s*$"),          # "1. Section Name:"
    re.compile(r"^((?:Kharif|Rabi|Zaid|Fertilizer|Water|Pest|Varieties?|Irrigat|Transplant|Sowing|NPK|Livestock|Fisheries?|GI Product)[^:\n]{0,60}):?\s*$", re.I),
]

MAX_CHUNK_WORDS = 150
CHUNK_OVERLAP_WORDS = 25

# ── Sub-topic taxonomy ────────────────────────────────────────────────────────
# Maps a canonical sub-topic tag to a list of trigger keywords/phrases.
# These are matched against the *section heading* of a chunk at index time.
_SUBTOPIC_RULES: List[Tuple[str, List[str]]] = [
    ("irrigation",   ["irrigat", "water", "watering", "awd", "drip", "flood", "moisture", "sinchayee"]),
    ("fertilizer",   ["fertilizer", "npk", "nitrogen", "phosphorus", "potassium", "urea", "dap",
                       "fym", "manure", "nutrient", "dose", "top dress", "basal", "micronutrient"]),
    ("sowing",       ["sowing", "sow", "planting", "planting time", "nursery", "transplant",
                       "seed rate", "seedling", "propagation", "spacing", "pit size"]),
    ("spacing",      ["spacing", "row gap", "plant distance", "seed rate", "pit size", "propagation"]),
    ("varieties",    ["variet", "hybrid", "cultivar", "variety", "recommended", "improved"]),
    ("pest",         ["pest", "insect", "bug", "thrips", "aphid", "mite", "borer", "armyworm",
                       "bollworm", "fly", "weevil", "beetle", "caterpillar"]),
    ("disease",      ["disease", "fungus", "fungal", "rust", "blight", "wilt", "mold", "virus",
                       "bacterial", "rot", "smut", "mildew", "spot", "pathogen"]),
    ("yield",        ["yield", "produce", "output", "production", "harvest", "tonnes", "quintal",
                       "per acre", "per hectare"]),
    ("soil",         ["soil", "land", "vertisol", "loam", "clay", "sandy", "pH", "alkaline",
                       "acidic", "organic carbon", "soil type"]),
    ("eligibility",  ["eligib", "who can", "entitled", "beneficiar", "qualify", "criteria",
                       "condition", "loanee", "landholding"]),
    ("cost",         ["subsid", "amount", "premium", "rate", "cost", "wage", "salary", "payment",
                       "financial", "assistance", "benefit", "compensation", "incentive"]),
    ("application",  ["apply", "application", "document", "required", "enrol", "register",
                       "portal", "form", "submit", "procedure", "process", "step"]),
    ("health-protocol", ["protocol", "procedure", "dose", "schedule", "antenatal", "anc",
                          "vaccination", "immuniz", "ors", "treatment", "first aid", "referral",
                          "symptom", "danger sign"]),
    ("legal-rights", ["right", "entitlement", "guarantee", "legal", "act", "helpline",
                       "grievance", "redressal", "complaint", "ombudsman"]),
]

def _tag_subtopic(section_label: str, chunk_body: str) -> str:
    """
    Assign a sub-topic tag to a chunk based on its section label + first 120 chars.
    Returns the first matching tag, or 'general' if nothing matches.
    """
    combined = (section_label + " " + chunk_body[:120]).lower()
    for tag, triggers in _SUBTOPIC_RULES:
        if any(t in combined for t in triggers):
            return tag
    return "general"


# ── Intent keyword → sub-topic map used at QUERY time ──────────────────────
# Each entry: (list_of_query_trigger_phrases, sub_topic_tag)
_INTENT_KEYWORD_MAP: List[Tuple[List[str], str]] = [
    # Irrigation / water
    (["water", "irrigat", "how often", "how frequently", "awd", "days between watering",
      "how many irrigations", "flood", "drip", "moisture", "sinchayee"], "irrigation"),
    # Fertilizer / NPK
    (["fertilizer", "npk", "nitrogen", "urea", "dap", "nutrient", "dose", "dosage",
      "how much to apply", "top dress", "basal", "manure", "micronutrient",
      "zinc", "boron", "iron deficiency", "sulfur", "when to add urea"], "fertilizer"),
    # Sowing / planting / nursery
    (["when to sow", "sowing", "planting time", "sow", "nursery", "transplant",
      "best time to plant", "when should i plant", "season to plant"], "sowing"),
    # Spacing / seed rate
    (["spacing", "distance between", "row gap", "seed rate", "plant distance",
      "how far apart", "how close"], "spacing"),
    # Varieties / hybrids
    (["variet", "hybrid", "which variety", "best variety", "recommended variety",
      "cultivar", "improved variety"], "varieties"),
    # Pests / insects
    (["pest", "insect", "bug", "thrips", "aphid", "mite", "borer", "armyworm",
      "bollworm", "fly", "weevil", "beetle", "caterpillar", "infestation",
      "insect attack", "bugs on"], "pest"),
    # Disease / fungal
    (["disease", "fungus", "fungal", "rust", "blight", "wilt", "mold", "virus",
      "bacterial", "rot", "smut", "mildew", "spot", "infection", "treatment for disease",
      "spray for disease"], "disease"),
    # Yield / output
    (["yield", "how much produce", "output per acre", "production", "quintal",
      "tonnes", "how much harvest", "how much i get"], "yield"),
    # Soil type / land
    (["soil type", "which soil", "best soil", "land type", "soil pH",
      "alkaline soil", "acidic soil", "vertisol", "loam", "clay soil"], "soil"),
    # Scheme eligibility
    (["eligible", "who can apply", "criteria", "who qualifies", "am i eligible",
      "entitled", "beneficiar", "qualify for"], "eligibility"),
    # Scheme cost / subsidy amount
    (["subsidy amount", "how much money", "how much subsidy", "how much help",
      "financial assistance", "benefit amount", "how much do i get",
      "how much is paid", "wage rate", "cost", "premium"], "cost"),
    # Application / documents / process
    (["how to apply", "documents needed", "documents required", "application process",
      "how do i apply", "what documents", "enrol", "register", "form to fill"], "application"),
    # Health / medical protocols
    (["vaccination", "vaccine", "immuniz", "bcg", "opv", "dpt", "antenatal",
      "anc", "asha", "maternal", "ors", "dehydration", "snake bite", "heat stroke",
      "first aid", "malaria", "symptoms", "treatment", "referral", "phc"], "health-protocol"),
    # Legal rights
    (["job card", "mgnrega", "nrega", "right to work", "helpline number",
      "legal aid", "free lawyer", "pahani", "rtc", "mutation", "land record"], "legal-rights"),
]


def _detect_query_subtopic(query: str) -> str | None:
    """
    Lightweight keyword scan of the query to detect user's sub-topic intent.
    Returns the matched sub-topic tag, or None if ambiguous.
    """
    q = query.lower()
    for triggers, tag in _INTENT_KEYWORD_MAP:
        if any(t in q for t in triggers):
            return tag
    return None


def _detect_section_label(line: str) -> str | None:
    """Return a clean section label if the line looks like a heading, else None."""
    line = line.strip()
    if not line or len(line) > 120:
        return None
    for pat in _HEADER_PATTERNS:
        m = pat.match(line)
        if m:
            return m.group(1).strip().rstrip(":")
    return None


def _split_into_sentences(text: str) -> List[str]:
    """Split a paragraph into sentences on .!? followed by space/newline."""
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def _word_count(text: str) -> int:
    return len(text.split())


def chunk_text(text: str, source_label: str = "") -> List[Tuple[str, str, str]]:
    """
    Semantic paragraph-aware chunker.

    Returns a list of (chunk_text, section_label, subtopic_tag) tuples.

    Algorithm:
    1. Split on blank lines to get paragraphs.
    2. Track the current section heading (any line that looks like a heading).
    3. Accumulate paragraph words into a chunk; flush when > MAX_CHUNK_WORDS.
    4. Prepend "[Source Label - Section Label] " to each chunk so keyword
       matching works even when the heading isn't repeated inside the chunk body.
    5. Tag each chunk with a sub-topic label for intent-aware boosting at query time.
    """
    paragraphs = re.split(r'\r?\n\s*\r?\n', text)
    chunks: List[Tuple[str, str, str]] = []

    current_section = source_label or "General"
    buffer_sentences: List[str] = []
    buffer_words = 0

    def flush_buffer(section: str):
        nonlocal buffer_sentences, buffer_words
        if not buffer_sentences:
            return
        body = " ".join(buffer_sentences)
        if source_label and source_label.lower() not in section.lower():
            full_section = f"{source_label} - {section}"
        else:
            full_section = section
        labeled = f"[{full_section}] {body}".strip()
        subtopic = _tag_subtopic(section, body)
        chunks.append((labeled, full_section, subtopic))
        # Overlap: keep last CHUNK_OVERLAP_WORDS words as seed for next chunk
        overlap_words = body.split()[-CHUNK_OVERLAP_WORDS:]
        buffer_sentences = [" ".join(overlap_words)] if overlap_words else []
        buffer_words = len(overlap_words)

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        lines = para.splitlines()
        para_lines_clean = []

        for line in lines:
            label = _detect_section_label(line)
            if label:
                # This line is a heading — flush current buffer under old section first
                flush_buffer(current_section)
                current_section = label
            else:
                para_lines_clean.append(line.strip())

        # Now process the non-header content lines as sentences
        para_body = " ".join(l for l in para_lines_clean if l)
        if not para_body:
            continue

        sentences = _split_into_sentences(para_body)
        for sent in sentences:
            sent_words = _word_count(sent)
            # If adding this sentence would overflow, flush first
            if buffer_words + sent_words > MAX_CHUNK_WORDS and buffer_sentences:
                flush_buffer(current_section)
            buffer_sentences.append(sent)
            buffer_words += sent_words

    flush_buffer(current_section)

    # Fallback: if nothing was produced, return the whole text as one chunk
    if not chunks and text.strip():
        subtopic = _tag_subtopic(source_label or "General", text[:120])
        chunks.append((text.strip(), source_label or "General", subtopic))

    return chunks


def init_store():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pack_id TEXT NOT NULL,
        filepath TEXT NOT NULL,
        section_label TEXT NOT NULL DEFAULT '',
        subtopic TEXT NOT NULL DEFAULT 'general',
        text_content TEXT NOT NULL,
        embedding BLOB NOT NULL
    )
    """)
    # Add columns if upgrading from old schema
    for col, default in [("section_label", "''"), ("subtopic", "'general'")]:
        try:
            cursor.execute(f"ALTER TABLE knowledge_chunks ADD COLUMN {col} TEXT NOT NULL DEFAULT {default}")
        except Exception:
            pass  # column already exists

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pack_id ON knowledge_chunks(pack_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_subtopic ON knowledge_chunks(subtopic)")
    conn.commit()
    conn.close()


def index_file(pack_id: str, filepath: str, text_content: str):
    init_store()

    # Derive a readable source label from the filename
    basename = os.path.splitext(os.path.basename(filepath))[0]
    source_label = basename.replace("_", " ").replace("-", " ").title()

    chunk_tuples = chunk_text(text_content, source_label=source_label)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if this file is already indexed (avoid duplicates on hot reload)
    cursor.execute(
        "SELECT COUNT(*) FROM knowledge_chunks WHERE pack_id = ? AND filepath = ?",
        (pack_id, filepath)
    )
    already_indexed = cursor.fetchone()[0]
    if already_indexed > 0:
        conn.close()
        return  # Skip — already in DB, use reindex_all.py to rebuild from scratch

    for chunk_body, section_label, subtopic in chunk_tuples:
        vector = get_embedding(chunk_body)
        vector_f32 = np.array(vector, dtype=np.float32)
        vector_bytes = vector_f32.tobytes()

        cursor.execute("""
        INSERT INTO knowledge_chunks (pack_id, filepath, section_label, subtopic, text_content, embedding)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (pack_id, filepath, section_label, subtopic, chunk_body, vector_bytes))

    conn.commit()
    conn.close()


def remove_pack_indices(pack_id: str):
    init_store()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM knowledge_chunks WHERE pack_id = ?", (pack_id,))
    conn.commit()
    conn.close()


# ── Crop alias table ──────────────────────────────────────────────────────────
_CROP_ALIASES: Dict[str, List[str]] = {
    "corn": ["corn", "maize"],
    "maize": ["corn", "maize"],
    "wheat": ["wheat"],
    "rice": ["rice", "paddy"],
    "paddy": ["rice", "paddy"],
    "ragi": ["ragi", "finger millet", "millet"],
    "bajra": ["bajra", "pearl millet"],
    "jowar": ["jowar", "sorghum"],
    "millet": ["millet", "bajra", "jowar", "ragi"],
    "sugarcane": ["sugarcane", "cane"],
    "cotton": ["cotton"],
    "groundnut": ["groundnut", "peanut"],
    "peanut": ["groundnut", "peanut"],
    "tur": ["tur", "pigeon pea", "arhar"],
    "pigeon": ["tur", "pigeon pea", "arhar"],
    "arhar": ["tur", "pigeon pea", "arhar"],
    "sunflower": ["sunflower"],
    "soybean": ["soybean", "soya", "soy"],
    "soya": ["soybean", "soya", "soy"],
    "chickpea": ["chickpea", "gram", "chana"],
    "gram": ["chickpea", "gram", "chana"],
    "chana": ["chickpea", "gram", "chana"],
    "mustard": ["mustard", "rapeseed", "rai", "sarson"],
    "barley": ["barley", "jau"],
    "banana": ["banana", "plantain", "kela"],
    "tomato": ["tomato"],
    "onion": ["onion", "pyaz"],
    "potato": ["potato", "aloo"],
    "coffee": ["coffee"],
    "tea": ["tea"],
    "rubber": ["rubber"],
    "apple": ["apple"],
    "cardamom": ["cardamom"],
    "pepper": ["pepper"],
}


def search_chunks(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Hybrid Search: Vector Cosine Similarity + Keyword Salience Boosting
    + Sub-topic Intent Boosting.

    Pipeline:
    1. Embed query, fetch all chunks.
    2. Detect crop in query → cross-crop mismatch penalty.
    3. Detect sub-topic intent in query → same-subtopic boost.
    4. Keyword match boost (unchanged).
    5. Sort by final_score and return top_k.
    """
    init_store()
    query_vector = get_embedding(query)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, pack_id, filepath, section_label, subtopic, text_content, embedding FROM knowledge_chunks")
    rows = cursor.fetchall()
    conn.close()

    # Extract content keywords (ignoring stopwords)
    q_words = {w.lower().strip(".,;:!?()[]{}'\"-") for w in query.split()} - STOPWORDS
    q_words = {qw for qw in q_words if len(qw) > 2}

    # Detect crop terms in query
    query_lower = query.lower()
    target_crop_synonyms: set = set()
    for crop_key, synonyms in _CROP_ALIASES.items():
        if re.search(r'\b' + re.escape(crop_key) + r'\b', query_lower):
            target_crop_synonyms.update(synonyms)

    # Detect sub-topic intent in query
    query_subtopic = _detect_query_subtopic(query)

    results = []
    for row in rows:
        cid, pack_id, filepath, section_label, subtopic, text, emb_bytes = row
        emb_vector = np.frombuffer(emb_bytes, dtype=np.float32)

        # Base vector similarity
        base_score = cosine_similarity(query_vector, emb_vector)

        text_lower = text.lower()

        # Cross-crop mismatch check
        crop_mismatch = False
        if target_crop_synonyms:
            if not any(syn in text_lower for syn in target_crop_synonyms):
                crop_mismatch = True

        # Keyword match boost
        if crop_mismatch:
            keyword_boost = 0.0
        else:
            keyword_hits = sum(1 for qw in q_words if qw in text_lower)
            if "KP-AGRI-STATE" in filepath:
                keyword_boost = keyword_hits * 0.08   # low — state metadata
            else:
                keyword_boost = keyword_hits * 0.18   # higher — cultivation/legal/health guides

        # Sub-topic intent boost: prefer chunks whose sub-topic matches detected intent
        subtopic_boost = 0.0
        if query_subtopic and not crop_mismatch:
            if subtopic == query_subtopic:
                subtopic_boost = 0.20   # Strong boost for exact sub-topic match
            elif _subtopics_related(query_subtopic, subtopic):
                subtopic_boost = 0.07   # Mild boost for related sub-topics

        # Dedicated-document specificity boost:
        # When the query names a crop, chunks from a file whose filename *explicitly*
        # contains the primary crop term are boosted vs generic cross-topic docs
        # (e.g. soil_health.txt, pest_control.txt, integrated_pest_management_ipm.txt).
        # This prevents "urea dose for rice" from retrieving soil_health.txt instead
        # of rice_cultivation_karnataka.txt.
        doc_specificity_boost = 0.0
        if target_crop_synonyms and not crop_mismatch:
            fp_lower = filepath.lower().replace("\\", "/")
            fp_basename = fp_lower.split("/")[-1]  # just the filename
            if any(syn.replace(" ", "_") in fp_basename for syn in target_crop_synonyms):
                doc_specificity_boost = 0.25   # Dedicated per-crop document
            else:
                # Halve keyword_boost for generic cross-topic docs when a crop is detected.
                # Soil health, IPM, pest control, and subsidies docs mention all crops
                # incidentally — they should NOT outrank the dedicated cultivation guide.
                _GENERIC_DOCS = {
                    "soil_health", "pest_control", "organic_pest_control",
                    "integrated_pest_management_ipm", "agricultural_subsidies",
                    "multi_cropping", "pulses_india", "micronutrient_deficiency_guide",
                }
                if any(g in fp_basename for g in _GENERIC_DOCS):
                    keyword_boost *= 0.5

        final_score = base_score + keyword_boost + subtopic_boost + doc_specificity_boost
        if crop_mismatch:
            # Penalize cross-crop mismatch so wrong-crop docs trigger low-confidence fallback
            final_score = min(final_score, 0.25)

        results.append({
            "id": cid,
            "pack_id": pack_id,
            "filepath": filepath,
            "section_label": section_label,
            "subtopic": subtopic,
            "text": text,
            "score": final_score,
            "base_score": base_score,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def _subtopics_related(a: str, b: str) -> bool:
    """Return True if two sub-topic tags are semantically adjacent."""
    adjacency = {
        "irrigation": {"sowing", "yield"},
        "fertilizer": {"sowing", "soil", "yield", "micronutrient"},
        "sowing": {"spacing", "varieties", "irrigation"},
        "spacing": {"sowing", "varieties"},
        "varieties": {"sowing", "yield"},
        "pest": {"disease"},
        "disease": {"pest"},
        "yield": {"varieties", "fertilizer", "irrigation"},
        "soil": {"fertilizer"},
        "eligibility": {"cost", "application"},
        "cost": {"eligibility", "application"},
        "application": {"eligibility", "cost"},
        "health-protocol": {"legal-rights"},
        "legal-rights": {"health-protocol"},
    }
    return b in adjacency.get(a, set())
