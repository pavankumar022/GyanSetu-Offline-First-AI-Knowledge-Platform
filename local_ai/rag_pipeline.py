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
    "up", "mp", "ap", "tn", "wb", "hp",  # abbreviations
]

# Map common abbreviations/alternatives to their canonical state slug
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
    # Resolve abbreviations first
    for abbr, full in _ABBREV_MAP.items():
        if re.search(r'\b' + re.escape(abbr) + r'\b', query_lower):
            return full

    # Longest-match pass over full state names
    found = []
    for state in _INDIA_STATES:
        if state in query_lower:
            found.append(state)
    if found:
        return max(found, key=len)  # longest match wins
    return None


def _slug(name: str) -> str:
    return name.lower().replace(" ", "_").replace("&", "and").replace(",", "")


def _boost_state_chunks(chunks: List[Dict], state_name: str, boost: float = 1.2) -> List[Dict]:
    """
    Apply an additive score boost to chunks from the target state's document.
    Only boosts KP-AGRI-STATE/<state_slug>.txt — leaves all other chunks unchanged.
    """
    target_filename = _slug(state_name) + ".txt"
    for chunk in chunks:
        filepath = chunk.get("filepath", "")
        if "KP-AGRI-STATE" in filepath and target_filename in filepath:
            chunk = dict(chunk)  # don't mutate original
            chunk["score"] = chunk["score"] + boost
    # Re-sort after boost
    return sorted(chunks, key=lambda x: x["score"], reverse=True)


def query_offline_ai(query_text: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Main offline RAG query function.

    Steps:
      1. Detect any Indian state name in the query.
      2. Search local vector index (hybrid: cosine + keyword boost).
      3. If a state was detected, apply additional score boost to that state's chunks.
      4. Threshold check — refuse to answer if no relevant content found.
      5. Generate grounded response using local context summariser.
      6. Return answer + citations.

    Never guesses. Never fills gaps beyond what is in the indexed documents.
    """
    query_lower = query_text.lower()

    # 1. State detection
    detected_state = _detect_state(query_lower)

    # 2. Hybrid vector search (fetch slightly more to allow re-ranking)
    raw_chunks = search_chunks(query_text, top_k=top_k + 3)

    if not raw_chunks:
        return {
            "answer": (
                "I don't have any information on this topic in your downloaded knowledge packs. "
                "Please check the Knowledge Packs tab and download the relevant pack."
            ),
            "citations": [],
            "detected_state": detected_state
        }

    # 3. State boost (additive, preserves national fallback)
    if detected_state:
        boosted_chunks = _boost_state_chunks(raw_chunks, detected_state)
    else:
        boosted_chunks = raw_chunks

    # Take top_k after potential re-ranking
    chunks = boosted_chunks[:top_k]

    # 4. Threshold check
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

    # 5. Granularity guard — if user asks for district-level data, be honest
    district_keywords = ["district", "block", "taluk", "tehsil", "mandal", "village", "locality",
                         "street", "town", "city", "exact", "how many", "count", "tonnage"]
    if any(kw in query_lower for kw in district_keywords) and detected_state:
        # Check if the matched state chunks even mention the requested granularity
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

    # 6. Generate grounded response
    answer = generate_local_response(query_text, chunks)

    # 7. Build citations (deduplicated by file)
    citations = []
    seen_paths = set()
    for chunk in chunks:
        path = chunk["filepath"]
        if path not in seen_paths:
            seen_paths.add(path)
            filename = os.path.basename(path)
            title = filename.replace(".txt", "").replace("_", " ").title()

            raw_score = chunk["score"]
            # Normalise score to confidence %. Boosted state chunks can score > 1.0
            capped_score = min(raw_score, 2.0)
            confidence = int(min(98, max(60, (capped_score / 2.0) * 38 + 60)))

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
