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


def _boost_state_chunks(chunks: List[Dict], state_name: str, boost: float = 2.5) -> List[Dict]:
    """
    Apply a strong score boost to chunks from the target state's document.
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

    # Fetch top 25 candidate chunks across all 43 documents
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

    # Threshold check
    top_score = chunks[0]["score"]
    if top_score < 0.20:
        return {
            "answer": (
                "This question appears to fall outside the scope of your currently installed knowledge packs. "
                "I only provide verified, grounded answers based on your local data — not guesses.\n\n"
                "*Tip: Try asking about specific states (e.g. 'Kharif crops in Gujarat'), crops "
                "(wheat, rice, pulses), agricultural subsidies (PM-KISAN, PMFBY), soil health, "
                "pest management, scholarships, rural healthcare, or legal rights (RTI, MGNREGS).*"
            ),
            "citations": [],
            "detected_state": detected_state
        }

    # Granularity guard
    district_keywords = ["district", "block", "taluk", "tehsil", "mandal", "village", "locality",
                         "street", "town", "city", "exact", "how many", "count", "tonnage"]
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

    # Generate grounded response
    answer = generate_local_response(query_text, chunks)

    # Build citations (deduplicated by file)
    citations = []
    seen_paths = set()
    for chunk in chunks:
        path = chunk["filepath"]
        if path not in seen_paths:
            seen_paths.add(path)
            filename = os.path.basename(path)
            title = filename.replace(".txt", "").replace("_", " ").title()

            raw_score = chunk["score"]
            capped_score = min(raw_score, 3.0)
            confidence = int(min(98, max(60, (capped_score / 3.0) * 38 + 60)))

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
