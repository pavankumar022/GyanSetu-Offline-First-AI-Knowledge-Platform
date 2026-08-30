"""
llm_client.py — GyanSetu Answer Synthesis Engine (v3.0 — Intent-Aware)
──────────────────────────────────────────────────────────────────────────────
Generates precise, right-sized answers by:

1. Classifying query intent: NARROW (specific fact) or BROAD (overview).
2. Detecting the exact sub-topic the user is asking about (irrigation,
   fertilizer, sowing-time, pest, disease, yield, eligibility, cost, etc.)
   using a keyword map + sub-topic of top-ranked chunk as confirmation.
3. NARROW + sub-topic detected → extract ONLY sentences matching that
   sub-topic from the top chunks. Never mix sub-topics into the answer.
4. BROAD → build a structured multi-section summary, de-duplicated by section.
5. Returns (answer_text, used_chunk_ids) for accurate citation building.

SYNTHESIS RULE (enforced in all paths):
  "Answer exactly what was asked. Use specific numbers/dates/facts from the
   context. Do NOT include information about other sub-topics (e.g. pest info
   when irrigation was asked). Keep the answer to a few sentences unless the
   question is broad."
──────────────────────────────────────────────────────────────────────────────
"""

import os
import re
from typing import List, Dict, Tuple, Any

_llm = None
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "device_storage", "models")

# ── Intent classifier patterns ────────────────────────────────────────────────
_NARROW_PATTERNS = [
    r'\bhow many\b', r'\bhow long\b', r'\bhow much\b', r'\bwhen (do|should|to)\b',
    r'\bwhat (dose|dosage|rate|amount|quantity|npk|ratio)\b',
    r'\bhow (do|can|should) i\b',
    r'\b(days?|weeks?|months?)\b.*\b(sow|transplant|harvest|sowing|planting)\b',
    r'\b(transplant|sow|plant|harvest)\b.*\b(days?|weeks?|when)\b',
    r'\bdifference between\b', r'\bcompare\b', r'\bvs\b',
    r'\bfirst aid\b', r'\btreatment for\b', r'\bapplication (rate|dose)\b',
    r'\beligib\b', r'\bapply for\b', r'\bscheme benefit\b',
    r'\bwhat is (the |a )?(npk|dose|amount|rate|benefit|penalty|fine)\b',
    r'\burea\b', r'\birrigat\b', r'\bwater\b.*\b(crop|rice|maize|wheat|paddy)\b',
    r'\bspacing\b', r'\brow (gap|distance)\b', r'\bseed rate\b',
    r'\bpremium\b', r'\bwage\b', r'\bsubsid\b',
]

_BROAD_PATTERNS = [
    r'^tell me (about|all about)\b',
    r'^(explain|describe|overview of|summary of|what is|give me)\b.*\bcultivation\b',
    r'^(explain|describe)\b',
    r'\boverview\b', r'\bin (general|detail)\b',
    r'^what (are|is) (the )?(major|main|key|important|different|various)\b',
]

# ── Sub-topic extraction keyword map ─────────────────────────────────────────
# At synthesis time, use these to score individual sentences for relevance.
_SUBTOPIC_KEYWORDS: Dict[str, List[str]] = {
    "irrigation":   ["irrigat", "water", "watering", "flood", "awd", "drip",
                     "moisture", "sinchayee", "litre", "liter", "mm", "rainfed",
                     "how often", "how frequently", "days between", "stop irrigation", "water requirement",
                     "flowering", "silking", "tasseling", "critical", "stage"],
    "fertilizer":   ["fertilizer", "npk", "nitrogen", "phosphorus", "potassium",
                     "urea", "dap", "fym", "manure", "dose", "top dress", "basal",
                     "kg/ha", "kg per hectare", "micronutrient", "zinc", "boron",
                     "iron", "sulfur", "n:p:k", "n :p:k", "top-dressing"],
    "sowing":       ["sow", "planting", "nursery", "transplant", "season", "timing",
                     "when to", "optimal", "window", "june", "july", "october",
                     "november", "kharif", "rabi", "zaid", "germination", "sowing window"],
    "duration":     ["duration", "days", "months", "growth duration", "maturity duration",
                     "sowing to harvest", "total crop duration", "how long", "take to grow"],
    "harvest":      ["harvesting", "harvest", "maturity", "readiness", "moisture",
                     "yellow", "pods rattle", "yield", "post-harvest", "reap", "signs of maturity"],
    "season":       ["season", "kharif", "rabi", "zaid", "summer", "growing season",
                     "monsoon", "winter", "sowing window"],
    "spacing":      ["spacing", "distance", "row", "seed rate", "pit size",
                     "cm x cm", "plant per", "population", "density"],
    "varieties":    ["variet", "hybrid", "cultivar", "recommended", "improved",
                     "yield", "q/ha", "tonnes/ha", "duration", "maturity"],
    "pest":         ["pest", "insect", "aphid", "thrips", "mite", "borer",
                     "bollworm", "armyworm", "fly", "weevil", "beetle",
                     "caterpillar", "spray", "pheromone", "trap"],
    "disease":      ["disease", "fungus", "rust", "blight", "wilt", "mold",
                     "virus", "bacterial", "rot", "smut", "mildew", "spot",
                     "propiconazole", "mancozeb", "carbendazim", "fungicide"],
    "yield":        ["yield", "produce", "output", "production", "harvest",
                     "tonnes", "quintal", "per acre", "per hectare", "q/ha"],
    "soil":         ["soil", "land", "vertisol", "loam", "clay", "sandy",
                     "ph", "alkaline", "acidic", "organic carbon"],
    "eligibility":  ["eligib", "who can", "entitled", "beneficiar", "qualify",
                     "criteria", "condition", "loanee", "landholding",
                     "small", "marginal", "farmer family"],
    "cost":         ["subsid", "amount", "premium", "rate", "cost", "wage",
                     "salary", "payment", "financial", "assistance", "benefit",
                     "compensation", "incentive", "lakh", "crore", "rupee",
                     "rs.", "₹"],
    "application":  ["apply", "application", "document", "required", "enrol",
                     "register", "portal", "form", "submit", "procedure",
                     "process", "step", "channel", "aadhaar", "bank passbook"],
    "health-protocol": ["protocol", "dose", "schedule", "antenatal", "anc",
                         "vaccination", "immuniz", "ors", "treatment",
                         "first aid", "referral", "symptom", "danger sign",
                         "bcg", "opv", "dpt", "measles", "asha"],
    "legal-rights": ["right", "entitlement", "guarantee", "legal", "act",
                     "helpline", "grievance", "redressal", "complaint",
                     "ombudsman", "pahani", "rtc", "mutation", "job card"],
}


def _classify_intent(query: str) -> str:
    """Returns 'NARROW' or 'BROAD' based on linguistic patterns."""
    q = query.lower().strip()
    for pat in _NARROW_PATTERNS:
        if re.search(pat, q):
            return "NARROW"
    for pat in _BROAD_PATTERNS:
        if re.search(pat, q):
            return "BROAD"
    # Default: short query (≤ 8 words) → NARROW; longer → BROAD
    return "NARROW" if len(q.split()) <= 8 else "BROAD"


def _detect_synthesis_subtopic(query: str, top_chunk_subtopic: str | None) -> str | None:
    """
    Detect the sub-topic the user is asking about by:
    1. Scanning the query against _SUBTOPIC_KEYWORDS.
    2. If ambiguous, confirm with the top chunk's subtopic tag.
    Returns a sub-topic key from _SUBTOPIC_KEYWORDS, or None.
    """
    q = query.lower()
    best_tag = None
    best_hits = 0
    for tag, keywords in _SUBTOPIC_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in q)
        if hits > best_hits:
            best_hits = hits
            best_tag = tag

    if best_hits >= 1:
        return best_tag

    # Fall back to the chunk's sub-topic tag from retrieval
    return top_chunk_subtopic if top_chunk_subtopic and top_chunk_subtopic != "general" else None


def _query_keywords(query: str) -> set:
    """Return meaningful keywords from the query (no stopwords, len > 2)."""
    STOPWORDS = {
        "a", "about", "after", "all", "am", "an", "and", "any", "are", "as", "at",
        "be", "been", "before", "between", "but", "by", "can", "could", "do", "does",
        "doing", "during", "for", "from", "had", "has", "have", "how", "i", "if",
        "in", "into", "is", "it", "its", "just", "me", "more", "my", "no", "not",
        "now", "of", "on", "or", "other", "our", "out", "over", "should", "so",
        "some", "than", "that", "the", "their", "them", "then", "there", "these",
        "they", "this", "those", "through", "to", "too", "under", "up", "was", "we",
        "were", "what", "when", "where", "which", "while", "who", "why", "will",
        "with", "you", "your", "tell", "give", "explain", "describe", "need",
    }
    words = re.findall(r'[a-zA-Z]+', query.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def _sentence_relevance(sentence: str, query_keywords: set, subtopic_keywords: List[str] | None) -> float:
    """
    Score a sentence by:
    - query keyword overlap (base relevance)
    - sub-topic keyword hit bonus (ensures sub-topic specificity)
    - stage/phase exact match bonus (e.g. flowering, silking, basal, top-dressing)
    """
    sent_lower = sentence.lower()
    kw_hits = sum(1 for kw in query_keywords if kw in sent_lower)
    kw_score = kw_hits / max(len(query_keywords), 1)

    subtopic_bonus = 0.0
    if subtopic_keywords:
        st_hits = sum(1 for kw in subtopic_keywords if kw in sent_lower)
        subtopic_bonus = min(st_hits * 0.3, 0.6)  # cap bonus at 0.6

    # Stage/phase term direct match bonus
    stage_terms = {"flowering", "silking", "tasseling", "knee-high", "sowing", "basal",
                   "top-dressing", "harvest", "maturity", "dough", "initial", "middle",
                   "final", "cri", "pegging", "buttoning", "blossom"}
    matched_stages = query_keywords.intersection(stage_terms)
    stage_bonus = 0.0
    if matched_stages and any(term in sent_lower for term in matched_stages):
        stage_bonus = 0.50

    return kw_score + subtopic_bonus + stage_bonus


def _extract_relevant_sentences(
    chunk_text: str,
    query_keywords: set,
    subtopic_keywords: List[str] | None,
    max_sentences: int = 3,
) -> List[str]:
    """
    Extract the most relevant sentences from a chunk for a NARROW/sub-topic query.
    Prioritizes sentences matching the sub-topic over general keyword matches.
    """
    # Strip leading [Section Label] prefix
    clean_text = re.sub(r'^\[[^\]]+\]\s*', '', chunk_text.strip())

    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?•])\s+', clean_text)
    sentences = [
        s.strip() for s in sentences
        if s.strip()
        and len(s.split()) >= 4
        and not s.strip().startswith("Source:")
        and not s.strip().startswith("Source (")
        and not re.match(r'^\[[^\]]+\]\s*$', s.strip())  # bare [label] lines
    ]

    # Score each sentence
    scored = [
        (s, _sentence_relevance(s, query_keywords, subtopic_keywords))
        for s in sentences
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    # Take top-N, preserving original document order
    top_sents = {s for s, sc in scored[:max_sentences] if sc > 0}
    if not top_sents:
        top_sents = {s for s, _ in scored[:2]}

    result = [s for s in sentences if s in top_sents]
    return result[:max_sentences]


def _format_section_label(chunk: Dict) -> str:
    """Get a clean display label for a chunk section."""
    sl = chunk.get("section_label", "").strip()
    if sl:
        return sl
    basename = os.path.splitext(os.path.basename(chunk.get("filepath", "unknown")))[0]
    return basename.replace("_", " ").replace("-", " ").title()


def _build_followup(query: str, detected_subtopic: str | None) -> str:
    """Build a contextual follow-up suggestion based on sub-topic."""
    q_lower = query.lower()
    hints = []
    if detected_subtopic == "irrigation":
        hints = ["fertilizer schedule", "pest management"]
    elif detected_subtopic == "fertilizer":
        hints = ["irrigation timings", "pest management"]
    elif detected_subtopic == "sowing":
        hints = ["variety recommendations", "fertilizer schedule"]
    elif detected_subtopic == "spacing":
        hints = ["seed rate", "sowing season"]
    elif detected_subtopic == "varieties":
        hints = ["sowing time", "yield expectations"]
    elif detected_subtopic == "pest":
        hints = ["disease management", "organic pest control"]
    elif detected_subtopic == "disease":
        hints = ["pest management", "soil health"]
    elif detected_subtopic == "yield":
        hints = ["fertilizer dose", "irrigation requirements"]
    elif detected_subtopic == "eligibility":
        hints = ["required documents", "how to apply"]
    elif detected_subtopic == "cost":
        hints = ["eligibility criteria", "how to apply"]
    elif detected_subtopic == "application":
        hints = ["eligibility criteria", "benefit amounts"]
    elif detected_subtopic == "health-protocol":
        hints = ["referral symptoms", "ORS protocol"]
    elif detected_subtopic == "legal-rights":
        hints = ["helpline numbers", "grievance process"]
    elif "subsid" in q_lower or "scheme" in q_lower or "pm-kisan" in q_lower:
        hints = ["eligibility criteria", "how to apply"]
    else:
        hints = ["more details on this topic"]

    hint_str = " or ".join(hints[:2])
    return f"\n\n*Want more on {hint_str}? Just ask.*"


def _synthesize_narrow(query: str, chunks: List[Dict], detected_subtopic: str | None) -> Tuple[str, List[int]]:
    """
    For NARROW queries: extract the most relevant sentences, filtered by
    the detected sub-topic. Answers ONLY the specific sub-topic asked about.
    Returns (answer_text, used_chunk_ids).
    """
    query_keywords = _query_keywords(query)
    subtopic_keywords = _SUBTOPIC_KEYWORDS.get(detected_subtopic, []) if detected_subtopic else None

    used_ids: List[int] = []
    best_sentences: List[str] = []

    for chunk in chunks:
        sents = _extract_relevant_sentences(
            chunk["text"], query_keywords, subtopic_keywords, max_sentences=3
        )
        if sents:
            if chunk.get("id") is not None:
                used_ids.append(chunk["id"])
            best_sentences.extend(sents)
        if len(best_sentences) >= 4:
            break

    if not best_sentences:
        # Fallback: take first 3 sentences of top chunk
        top_text = chunks[0]["text"].strip()
        sents = re.split(r'(?<=[.!?•])\s+', top_text)
        best_sentences = [s.strip() for s in sents[:3] if s.strip()]
        used_ids = [chunks[0]["id"]] if chunks[0].get("id") else []

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for s in best_sentences:
        if s not in seen:
            seen.add(s)
            deduped.append(s)

    answer_body = " ".join(deduped[:3])
    followup = _build_followup(query, detected_subtopic)
    return answer_body + followup, used_ids


def _synthesize_broad(query: str, chunks: List[Dict]) -> Tuple[str, List[int]]:
    """
    For BROAD queries: build a structured multi-section summary.
    Returns (answer_text, used_chunk_ids).
    """
    used_ids: List[int] = []
    sections_seen: set = set()
    lines: List[str] = []

    lines.append("**GyanSetu Knowledge Summary**\n")

    for chunk in chunks:
        section = _format_section_label(chunk)
        if section in sections_seen:
            continue
        sections_seen.add(section)

        if chunk.get("id") is not None:
            used_ids.append(chunk["id"])

        chunk_body = chunk["text"].strip()
        # Remove the leading [Section Label] prefix if present
        chunk_body = re.sub(r'^\[[^\]]+\]\s*', '', chunk_body)

        # Break into bullets on • or line breaks
        raw_bullets = re.split(r'[•\n]+', chunk_body)
        bullets = [
            b.strip(" \t-–—") for b in raw_bullets
            if b.strip()
            and len(b.strip()) > 12
            and not b.strip().startswith("Source:")
            and not b.strip().startswith("Source (")
            and not b.strip().lower().startswith("administrative type:")
            and not b.strip().lower().startswith("coverage:")
        ]

        if bullets:
            lines.append(f"\n**{section}**")
            for b in bullets[:5]:  # Max 5 bullets per section
                lines.append(f"• {b}")

    if not lines or len(lines) <= 1:
        return chunks[0]["text"].strip(), [chunks[0]["id"]] if chunks[0].get("id") else []

    return "\n".join(lines), used_ids


# ── Main entry point ─────────────────────────────────────────────────────────

def get_llm_model():
    global _llm
    if _llm is not None:
        return _llm

    os.makedirs(MODELS_DIR, exist_ok=True)
    gguf_files = [f for f in os.listdir(MODELS_DIR) if f.endswith(".gguf")]

    if not gguf_files:
        _llm = "fallback"
        return _llm

    model_path = os.path.join(MODELS_DIR, gguf_files[0])
    try:
        from llama_cpp import Llama
        _llm = Llama(model_path=model_path, n_ctx=2048, verbose=False)
    except Exception:
        _llm = "fallback"

    return _llm


def generate_local_response(query: str, context_chunks: List[Dict]) -> Tuple[str, List[int]]:
    """
    Generate a synthesized offline response.

    Returns:
        (answer_text, used_chunk_ids)
        used_chunk_ids: list of chunk DB IDs whose content was used.
    """
    model = get_llm_model()

    if not context_chunks:
        return (
            "I don't have this information in my offline knowledge packs. "
            "Please check the Knowledge Packs tab and download the relevant pack.",
            []
        )

    # Detect intent and sub-topic
    intent = _classify_intent(query)
    top_chunk_subtopic = context_chunks[0].get("subtopic") if context_chunks else None
    detected_subtopic = _detect_synthesis_subtopic(query, top_chunk_subtopic)

    if model == "fallback":
        if intent == "NARROW":
            return _synthesize_narrow(query, context_chunks, detected_subtopic)
        else:
            return _synthesize_broad(query, context_chunks)
    else:
        # Local LLM path (llama-cpp)
        try:
            # Build a precision-focused prompt
            subtopic_instruction = ""
            if detected_subtopic and detected_subtopic in _SUBTOPIC_KEYWORDS:
                related_kws = ", ".join(_SUBTOPIC_KEYWORDS[detected_subtopic][:6])
                subtopic_instruction = (
                    f" The user is specifically asking about: **{detected_subtopic}**. "
                    f"Focus ONLY on information related to: {related_kws}. "
                    f"Do NOT include information about other topics (e.g. pest info when irrigation was asked)."
                )

            if intent == "NARROW":
                instruction = (
                    "You are answering a specific question using only the provided context. "
                    "Identify exactly what the user is asking about (e.g. irrigation, fertilizer, "
                    "sowing time, eligibility, cost) and answer ONLY that, using specific "
                    "numbers/dates/facts from the context. Do not include unrelated information "
                    "from the context even if it is present. Keep the answer concise — a few "
                    "sentences. If the context does not contain the answer to the specific question "
                    "asked, say so rather than answering a related but different question."
                ) + subtopic_instruction
            else:
                instruction = (
                    "Provide a structured summary using the provided context. "
                    "Use bold section headers for each sub-topic. Be comprehensive but do not "
                    "repeat verbatim paragraphs. Organize by clear sub-headings."
                ) + subtopic_instruction

            system_prompt = f"You are GyanSetu AI, an offline knowledge assistant. {instruction}"
            full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\nContext:\n"
            for chunk in context_chunks:
                full_prompt += f"Source: {chunk.get('section_label','')}\nContent: {chunk['text']}\n---\n"
            full_prompt += f"\nQuestion: {query}\n<|assistant|>\n"

            output = model(full_prompt, max_tokens=300, stop=["<|user|>", "<|system|>"], echo=False)
            answer = output['choices'][0]['text'].strip()
            used_ids = [c["id"] for c in context_chunks if c.get("id") is not None]
            return answer, used_ids
        except Exception as e:
            return f"Error during local model inference: {e}", []
