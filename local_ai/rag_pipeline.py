import os
from typing import Dict, Any, List
from local_ai.vector_store import search_chunks
from local_ai.llm_client import generate_local_response
from local_ai.embeddings import STOPWORDS

# Known locations and geographical entities to detect out-of-scope location queries
KNOWN_REGIONS = {
    "mumbai": "Mumbai (Maharashtra - Konkan coastal zone)",
    "maharashtra": "Maharashtra",
    "delhi": "Delhi / NCR",
    "punjab": "Punjab",
    "haryana": "Haryana",
    "tamil nadu": "Tamil Nadu",
    "chennai": "Chennai",
    "kerala": "Kerala",
    "rajasthan": "Rajasthan",
    "gujarat": "Gujarat",
    "bihar": "Bihar",
    "uttar pradesh": "Uttar Pradesh",
    "bengal": "West Bengal",
    "kolkata": "Kolkata",
    "hyderabad": "Hyderabad",
    "telangana": "Telangana",
    "andhra": "Andhra Pradesh"
}

def query_offline_ai(query_text: str, top_k: int = 2) -> Dict[str, Any]:
    query_lower = query_text.lower()
    
    # 1. Check for specific geographical mismatches
    detected_unsupported_locations = []
    for loc, loc_name in KNOWN_REGIONS.items():
        if loc in query_lower and loc not in ["karnataka", "dharwad", "belagavi", "bagalkot", "vijayapura", "gadag"]:
            detected_unsupported_locations.append(loc_name)
            
    # If user explicitly asked for Mumbai or another unsupported state/city
    if detected_unsupported_locations and "karnataka" not in query_lower:
        loc_str = ", ".join(detected_unsupported_locations)
        return {
            "answer": f"I do not have verified offline agricultural guidelines for **{loc_str}** in your currently installed knowledge packs.\n\n• **Installed Pack Coverage:** Agricultural Best Practices & Crop Data (covers Karnataka Zones 3 & 8 — Dharwad, Belagavi, Vijayapura, Bagalkot, Gadag).\n• **Agronomic Context:** Commercial wheat cultivation requires cool, dry winters and is unsuited to warm coastal humid regions like Mumbai.\n\n*Please download the relevant regional pack or search for Karnataka crop advisories.*",
            "citations": []
        }

    # 2. Search vector database for similar chunks
    chunks = search_chunks(query_text, top_k=top_k)
    
    if not chunks:
        return {
            "answer": "I don't have this information in my offline knowledge packs. Please verify if you have downloaded the relevant knowledge domain in the Knowledge Packs tab.",
            "citations": []
        }
    
    # 3. Check similarity threshold
    top_score = chunks[0]["score"]
    if top_score < 0.20:
        return {
            "answer": "This question appears to be outside the scope of your currently downloaded knowledge packs. I only provide verified answers based on local data without guessing.\n\n*Tip: Try asking about wheat cultivation in Karnataka, agricultural subsidies (PM-KISAN), soil pH treatment, or pest control.*",
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
            filename = os.path.basename(path)
            title = filename.replace(".txt", "").replace("_", " ").title()
            
            # Simulated confidence based on match score
            confidence = int(min(98, max(60, chunk["score"] * 100)))
            
            citations.append({
                "title": f"{title}",
                "filepath": path,
                "excerpt": chunk["text"][:220] + "...",
                "confidence": confidence
            })
            
    return {
        "answer": answer,
        "citations": citations
    }
