import os
import sqlite3
import numpy as np
from typing import List, Dict, Any
from local_ai.embeddings import get_embedding, cosine_similarity, STOPWORDS

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "device_storage")
DB_PATH = os.path.join(DB_DIR, "local_knowledge.db")

def init_store():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pack_id TEXT NOT NULL,
        filepath TEXT NOT NULL,
        text_content TEXT NOT NULL,
        embedding BLOB NOT NULL
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pack_id ON knowledge_chunks(pack_id)")
    conn.commit()
    conn.close()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
        if i >= len(words) - overlap:
            break
            
    if not chunks and text.strip():
        chunks.append(text)
        
    return chunks

def index_file(pack_id: str, filepath: str, text_content: str):
    init_store()
    chunks = chunk_text(text_content)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for chunk in chunks:
        vector = get_embedding(chunk)
        vector_f32 = np.array(vector, dtype=np.float32)
        vector_bytes = vector_f32.tobytes()
        
        cursor.execute("""
        INSERT INTO knowledge_chunks (pack_id, filepath, text_content, embedding)
        VALUES (?, ?, ?, ?)
        """, (pack_id, filepath, chunk, vector_bytes))
        
    conn.commit()
    conn.close()

def remove_pack_indices(pack_id: str):
    init_store()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM knowledge_chunks WHERE pack_id = ?", (pack_id,))
    conn.commit()
    conn.close()

def search_chunks(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Hybrid Search: Vector Cosine Similarity + Keyword Salience Boosting."""
    init_store()
    query_vector = get_embedding(query)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, pack_id, filepath, text_content, embedding FROM knowledge_chunks")
    rows = cursor.fetchall()
    conn.close()
    
    # Extract query content keywords (ignoring stopwords)
    q_words = {w.lower().strip(".,;:!?()[]{}'\"") for w in query.split()} - STOPWORDS
    q_words = {qw for qw in q_words if len(qw) > 2}
    
    results = []
    for row in rows:
        cid, pack_id, filepath, text, emb_bytes = row
        emb_vector = np.frombuffer(emb_bytes, dtype=np.float32)
        
        # Base vector similarity
        base_score = cosine_similarity(query_vector, emb_vector)
        
        # Keyword match boost
        text_lower = text.lower()
        keyword_hits = sum(1 for qw in q_words if qw in text_lower)
        
        # Final combined score
        final_score = base_score + (keyword_hits * 0.35)
        
        results.append({
            "id": cid,
            "pack_id": pack_id,
            "filepath": filepath,
            "text": text,
            "score": final_score
        })
        
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
