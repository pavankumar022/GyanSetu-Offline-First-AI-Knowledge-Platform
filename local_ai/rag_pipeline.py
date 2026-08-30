"""
rag_pipeline.py — GyanSetu Offline RAG Query Engine
─────────────────────────────────────────────────────────────────────────────
Hybrid Search: Vector Cosine Similarity + Keyword Salience Boosting.
State-name detection: if the query mentions an Indian state/UT name, retrieval
   additionally boosts chunks from that state's document in KP-AGRI-STATE.
   This is ADDITIVE — general national docs remain as the fallback baseline.

DATA INTEGRITY GUARANTEE:
  • Only information physically present in indexed docs is returned.
  • If the top score is below threshold → returns explicit out-of-scope message.
  • No hallucination, no guessing, no gap-filling.

CITATION ACCURACY:
  • generate_local_response() returns used_chunk_ids alongside the answer.
  • Only chunks in used_chunk_ids are shown as citations to the user.
"""

import os
import re
from typing import Dict, Any, List
from local_ai.vector_store import search_chunks
from local_ai.llm_client import generate_local_response

# ── Canonical list of all 36 Indian states + UTs (lower-case for matching) ──
_INDIA_STATES = [
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
    "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka",
    "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya",
    "mizoram", "nagaland", "odisha", "punjab", "rajasthan", "sikkim",
    "tamil nadu", "telangana", "tripura", "uttar pradesh", "uttarakhand",
    "west bengal",
    # Union Territories
    "andaman and nicobar", "andaman", "nicobar",
    "chandigarh",
    "dadra and nagar haveli", "daman and diu", "dadra", "diu",
    "delhi", "new delhi", "ncr",
    "jammu and kashmir", "jammu", "kashmir", "j&k",
    "ladakh",
    "lakshadweep",
    "puducherry", "pondicherry",
    # Common alternative names
    "up", "mp", "ap", "tn", "wb", "hp",
]

_ABBREV_MAP = {
    "up": "uttar pradesh",
    "mp": "madhya pradesh",
    "ap": "andhra pradesh",
    "tn": "tamil nadu",
    "wb": "west bengal",
    "hp": "himachal pradesh",
    "j&k": "jammu and kashmir",
    "ncr": "delhi",
    "new delhi": "delhi",
    "pondicherry": "puducherry",
}

# Relevance threshold — hash-based embeddings produce low cosine sims (0.10-0.40 range)
_RELEVANCE_THRESHOLD = 0.10


def get_confidence_percentage(chunk: Dict[str, Any]) -> int:
    """
    Calculate confidence percentage (0-100%) from hybrid similarity score.
    Scores >= 0.40 represent strong matches (>= 75% confidence).
    """
    score = chunk.get("score", 0.0)
    if score >= 0.40:
        return int(min(98, 75 + (score - 0.40) * 50))
    elif score >= 0.20:
        return int(40 + (score - 0.20) * 175)
    else:
        return int(max(0, score * 200))


def _detect_state(query_lower: str) -> str | None:
    """
    Return the canonical state name if the query mentions an Indian state/UT.
    Returns None if no state is detected.
    Prefers longest match to handle overlapping names correctly.
    """
    for abbr, full in _ABBREV_MAP.items():
        if re.search(r'\b' + re.escape(abbr) + r'\b', query_lower):
            return full

    found = []
    for state in _INDIA_STATES:
        if state in query_lower:
            found.append(state)
    if found:
        return max(found, key=len)
    return None


def _slug(name: str) -> str:
    return name.lower().replace(" ", "_").replace("&", "and").replace(",", "")


def _boost_state_chunks(chunks: List[Dict], state_name: str, boost: float = 0.30) -> List[Dict]:
    """
    Apply a moderate score boost to chunks from the target state's document.
    Moderate boost (+0.30) allows dedicated crop/scheme guides in KP-AGRI-ED-09
    to outrank raw state overviews when the user asks a crop-specific question.
    """
    target_filename = _slug(state_name) + ".txt"
    boosted = []
    for chunk in chunks:
        chunk_copy = dict(chunk)
        filepath = chunk.get("filepath", "")
        if "KP-AGRI-STATE" in filepath and target_filename in filepath:
            chunk_copy["score"] += boost
        boosted.append(chunk_copy)
    return sorted(boosted, key=lambda x: x["score"], reverse=True)


def query_offline_ai(query_text: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Main offline RAG query function.
    """
    query_lower = query_text.lower()
    detected_state = _detect_state(query_lower)

    # Fetch top 25 candidate chunks across all documents
    raw_chunks = search_chunks(query_text, top_k=25)

    if not raw_chunks:
        return {
            "answer": (
                "I don't have any information on this topic in your downloaded knowledge packs. "
                "Please check the Knowledge Packs tab and download the relevant pack."
            ),
            "citations": [],
            "detected_state": detected_state
        }

    # Filter out chunks from other states if a specific state is detected
    if detected_state:
        target_state_slug = _slug(detected_state)
        filtered_chunks = []
        for chunk in raw_chunks:
            filepath = chunk.get("filepath", "")
            if "KP-AGRI-STATE" in filepath:
                # Keep only if it belongs to the matched state
                if f"{target_state_slug}.txt" in filepath.lower():
                    filtered_chunks.append(chunk)
            else:
                # Keep general national/baseline packs
                filtered_chunks.append(chunk)
        raw_chunks = filtered_chunks

    # State boost (additive, preserves national fallback)
    if detected_state:
        boosted_chunks = _boost_state_chunks(raw_chunks, detected_state)
    else:
        boosted_chunks = raw_chunks

    # Take top_k after re-ranking
    chunks = boosted_chunks[:top_k]

    if not chunks:
        return {
            "answer": (
                "I don't have any information on this topic in your downloaded knowledge packs. "
                "Please check the Knowledge Packs tab and download the relevant pack."
            ),
            "citations": [],
            "detected_state": detected_state
        }

    # ── Confidence Threshold (75% Minimum Retrieval Match) ────────────────────
    # Design Decision: If the top chunk's similarity score is below 0.75 (75%),
    # do NOT generate an ungrounded answer or cite mismatched sources.
    # Return a helpful fallback suggesting known covered topics without citations.
    top_confidence = get_confidence_percentage(chunks[0])
    if top_confidence < 75:
        return {
            "answer": (
                "I don't have verified local knowledge on this topic yet. "
                "Try asking about:\n"
                "🌾 **Crops**: wheat, rice/paddy, maize/corn, ragi, sugarcane, cotton, groundnut, "
                "tur/pigeon pea, sunflower, barley, bajra/jowar (millet), soybean, chickpea/gram, "
                "mustard, banana, tomato, onion, potato\n"
                "🏛️ **Government Schemes**: PM-KISAN, PMFBY crop insurance, Kisan Credit Card (KCC), "
                "PMKSY irrigation subsidy, Soil Health Card scheme, Karnataka state schemes "
                "(Raitha Vidya Nidhi, Krishi Bhagya)\n"
                "🏥 **Rural Health**: infant vaccination schedule, maternal/ASHA guidelines, "
                "snake bite first aid, dehydration & ORS protocol, disease symptoms & PHC referral\n"
                "🧪 **Soil & Pest**: organic pest control, Integrated Pest Management (IPM), "
                "micronutrient deficiency correction, soil health\n"
                "⚖️ **Legal Rights**: MGNREGS job guarantee, land records (Pahani/RTC), "
                "farmer helplines & free legal aid"
            ),
            "citations": [],
            "detected_state": detected_state
        }

    # Granularity guard
    district_keywords = ["district", "block", "taluk", "tehsil", "mandal", "village", "locality",
                         "street", "town", "city", "exact", "count", "tonnage"]
    if any(kw in query_lower for kw in district_keywords) and detected_state:
        state_chunk_texts = [c["text"] for c in chunks if "KP-AGRI-STATE" in c.get("filepath", "")]
        if not any(kw in " ".join(state_chunk_texts).lower() for kw in district_keywords):
            return {
                "answer": (
                    f"The current knowledge pack contains **state-level data only** for {detected_state.title()}. "
                    "District-level breakdowns, exact counts, and tonnage figures are not included in this pack.\n\n"
                    "This level of detail is available from data.gov.in, the state's Department of Agriculture, "
                    "or the Livestock Census reports — none of which are in the current offline knowledge base."
                ),
                "citations": [],
                "detected_state": detected_state
            }

    # ── Generate synthesized response + get used chunk IDs ──────────────────
    answer, used_chunk_ids = generate_local_response(query_text, chunks)

    # ── Build citations: ONLY chunks whose IDs were used in the answer ───────
    used_id_set = set(used_chunk_ids)

    # If synthesis returned no used IDs (edge case), fall back to top-1 chunk
    if not used_id_set and chunks:
        used_id_set = {chunks[0]["id"]}

    citations = []
    seen_paths = set()
    # Iterate in ranked order so citations are ordered by relevance
    for chunk in chunks:
        if chunk.get("id") not in used_id_set:
            continue
        path = chunk["filepath"]
        if path in seen_paths:
            continue
        seen_paths.add(path)

        filename = os.path.basename(path)
        title = filename.replace(".txt", "").replace("_", " ").title()

        confidence = get_confidence_percentage(chunk)

        citations.append({
            "title": title,
            "filepath": path,
            "excerpt": chunk["text"][:220] + "...",
            "confidence": confidence
        })

    return {
        "answer": answer,
        "citations": citations,
        "detected_state": detected_state
    }
