import os
from typing import Dict, Any, List
from local_ai.vector_store import search_chunks
from local_ai.llm_client import generate_local_response

def query_offline_ai(query_text: str, top_k: int = 2) -> Dict[str, Any]:
    # 1. Search vector database for similar chunks
    chunks = search_chunks(query_text, top_k=top_k)
    
    # 2. Check if we have any database chunks
    if not chunks:
        return {
            "answer": "I don't have this information in my offline knowledge packs. Please make sure you have downloaded or updated your agricultural packs in the 'Knowledge Packs' section.",
            "citations": []
        }
    
    # 3. Check similarity threshold (RAG grounding check)
    # If the score of the top chunk is very low, it means the query is unrelated to the knowledge base.
    if chunks[0]["score"] < 0.10:
        return {
            "answer": "This question seems to be outside the scope of my currently downloaded knowledge packs. I can only provide verified answers based on the local databases. Please ask a question related to agricultural advisories, schemes, or soil health.",
            "citations": []
        }
        
    # 4. Generate grounded response using local AI runtime
    answer = generate_local_response(query_text, chunks)
    
    # 5. Extract unique citations from chunks
    citations = []
    seen_paths = set()
    for chunk in chunks:
        path = chunk["filepath"]
        if path not in seen_paths:
            seen_paths.add(path)
            # Create a user-friendly title
            filename = os.path.basename(path)
            title = filename.replace(".txt", "").replace("_", " ").title()
            
            # Simulated confidence based on cosine similarity score
            confidence = int(min(99, max(50, chunk["score"] * 100)))
            
            citations.append({
                "title": f"{title}",
                "filepath": path,
                "excerpt": chunk["text"][:180] + "...",
                "confidence": confidence
            })
            
    return {
        "answer": answer,
        "citations": citations
    }
