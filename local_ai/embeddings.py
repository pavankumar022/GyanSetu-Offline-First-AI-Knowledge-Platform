import numpy as np
import hashlib

_model = None
EMBEDDING_DIM = 384

# Standard stop words to prevent common filler words from skewing similarity math
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", 
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", 
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", 
    "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", 
    "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", 
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", 
    "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", 
    "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", 
    "why", "will", "with", "you", "your", "yours", "yourself", "yourselves"
}

def get_embedding_model():
    global _model
    if _model is not None:
        return _model
    
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Loaded sentence-transformers model successfully.")
    except Exception as e:
        _model = "fallback"
    return _model

def get_embedding(text: str) -> np.ndarray:
    model = get_embedding_model()
    if model == "fallback":
        # Hash Vectorizer with Stopword Filtering
        vector = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        words = text.lower().split()
        
        has_content_word = False
        for w in words:
            w_clean = "".join([c for c in w if c.isalnum()])
            if w_clean and w_clean not in STOPWORDS:
                has_content_word = True
                h_idx = int(hashlib.md5(w_clean.encode("utf-8")).hexdigest(), 16) % EMBEDDING_DIM
                vector[h_idx] += 1.0
                
        # If text consists only of stop words, fall back to all cleaned words
        if not has_content_word:
            for w in words:
                w_clean = "".join([c for c in w if c.isalnum()])
                if w_clean:
                    h_idx = int(hashlib.md5(w_clean.encode("utf-8")).hexdigest(), 16) % EMBEDDING_DIM
                    vector[h_idx] += 1.0
                    
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector
    else:
        vector = model.encode(text)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    return float(np.dot(v1, v2))
