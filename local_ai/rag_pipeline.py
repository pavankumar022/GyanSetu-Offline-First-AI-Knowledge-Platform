import os
from typing import Dict, Any, List
from local_ai.vector_store import search_chunks
from local_ai.llm_client import generate_local_response

def query_offline_ai(query_text: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Main offline RAG query function.
    
    Uses Hybrid Search (vector similarity + keyword salience) against local SQLite vector index.
    Returns a grounded answer with source citations.
    If no relevant content found above threshold, returns an honest out-of-scope message.
    Never guesses or hallucinates.
    """
    # 1. Search the local vector index
    chunks = search_chunks(query_text, top_k=top_k)

    if not chunks:
        return {
            "answer": "I don't have any information on this topic in your downloaded knowledge packs. Please check the Knowledge Packs tab and download the relevant pack for this topic.",
            "citations": []
        }

    # 2. Threshold check — avoid guessing when score is too low
    top_score = chunks[0]["score"]
    if top_score < 0.20:
        return {
            "answer": (
                "This question appears to fall outside the scope of your currently installed knowledge packs. "
                "I only provide verified, grounded answers based on your local data — not guesses.\n\n"
                "*Tip: Try asking about wheat, rice, or pulses cultivation; agricultural subsidies (PM-KISAN, PMFBY); "
                "soil pH management; integrated pest management; scholarships; rural healthcare first-aid; "
                "or legal rights (RTI, MGNREGS).*"
            ),
            "citations": []
        }

    # 3. Generate grounded response using local AI runtime
    answer = generate_local_response(query_text, chunks)

    # 4. Extract unique citations
    citations = []
    seen_paths = set()
    for chunk in chunks:
        path = chunk["filepath"]
        if path not in seen_paths:
            seen_paths.add(path)
            filename = os.path.basename(path)
            title = filename.replace(".txt", "").replace("_", " ").title()

            # Map confidence from hybrid score (0.2 baseline → 60%, 1.0 → 98%)
            raw_score = chunk["score"]
            confidence = int(min(98, max(60, (raw_score - 0.2) / 0.8 * 38 + 60)))

            citations.append({
                "title": title,
                "filepath": path,
                "excerpt": chunk["text"][:220] + "...",
                "confidence": confidence
            })

    return {
        "answer": answer,
        "citations": citations
    }
