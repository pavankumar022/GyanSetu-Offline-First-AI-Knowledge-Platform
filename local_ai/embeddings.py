import numpy as np
import hashlib

# Global variables for embedding model
_model = None
EMBEDDING_DIM = 384 # Dimension of all-MiniLM-L6-v2

def get_embedding_model():
    global _model
    if _model is not None:
        return _model
    
    try:
        from sentence_transformers import SentenceTransformer
        # Load the model locally. If not found, it downloads it.
        # Uses CPU by default.
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Loaded sentence-transformers model successfully.")
    except Exception as e:
        print(f"Failed to load sentence-transformers: {e}. Falling back to hash-based Bag-of-Words vectorizer.")
        _model = "fallback"
    return _model

def get_embedding(text: str) -> np.ndarray:
    model = get_embedding_model()
    if model == "fallback":
        # Hash Vectorizer (Bag of Words mapped to 384 dimensions)
        # This provides a realistic text similarity comparison without heavy model weights.
        vector = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        # Simple cleaning and tokenization
        words = text.lower().split()
        for w in words:
            # Strip common punctuation
            w_clean = "".join([c for c in w if c.isalnum()])
            if w_clean:
                # Generate deterministic index in range [0, 383]
                h_idx = int(hashlib.md5(w_clean.encode("utf-8")).hexdigest(), 16) % EMBEDDING_DIM
                vector[h_idx] += 1.0
                
        # Normalize vector to unit length
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector
    else:
        # Generate real embedding using sentence-transformers
        vector = model.encode(text)
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    # Since we normalize vectors, cosine similarity is just the dot product
    return float(np.dot(v1, v2))
