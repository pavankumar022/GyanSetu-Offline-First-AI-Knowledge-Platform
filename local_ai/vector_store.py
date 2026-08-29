import os
import sqlite3
import numpy as np
from typing import List, Dict, Any
from local_ai.embeddings import get_embedding, cosine_similarity

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "device_storage")
DB_PATH = os.path.join(DB_DIR, "local_knowledge.db")

def init_store():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create chunks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pack_id TEXT NOT NULL,
        filepath TEXT NOT NULL,
        text_content TEXT NOT NULL,
        embedding BLOB NOT NULL
    )
    """)
    
    # Create index on pack_id
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pack_id ON knowledge_chunks(pack_id)")
    
    conn.commit()
    conn.close()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Helper to split text into overlapping chunks."""
    words = text.split()
    chunks = []
    
    # Simple chunking by word count
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
        if i >= len(words) - overlap:
            break
            
    # If text is small, return it as a single chunk
    if not chunks and text.strip():
        chunks.append(text)
        
    return chunks

def index_file(pack_id: str, filepath: str, text_content: str):
    """Chunk and embed a single file, adding it to the local vector store."""
    init_store()
    chunks = chunk_text(text_content)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for chunk in chunks:
        # Generate embedding
        vector = get_embedding(chunk)
        # Convert vector (numpy array) to float32 and save as binary
        vector_f32 = np.array(vector, dtype=np.float32)
        vector_bytes = vector_f32.tobytes()
        
        cursor.execute("""
        INSERT INTO knowledge_chunks (pack_id, filepath, text_content, embedding)
        VALUES (?, ?, ?, ?)
        """, (pack_id, filepath, chunk, vector_bytes))
        
    conn.commit()
    conn.close()

def remove_pack_indices(pack_id: str):
    """Remove all chunks associated with a pack (used when deleting a pack)."""
    init_store()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM knowledge_chunks WHERE pack_id = ?", (pack_id,))
    conn.commit()
    conn.close()

def search_chunks(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Compare query embedding against all chunks in SQLite database and return top results."""
    init_store()
    query_vector = get_embedding(query)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, pack_id, filepath, text_content, embedding FROM knowledge_chunks")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        cid, pack_id, filepath, text, emb_bytes = row
        # Read vector back from binary bytes
        emb_vector = np.frombuffer(emb_bytes, dtype=np.float32)
        
        # Calculate similarity
        score = cosine_similarity(query_vector, emb_vector)
        
        results.append({
            "id": cid,
            "pack_id": pack_id,
            "filepath": filepath,
            "text": text,
            "score": score
        })
        
    # Sort results by similarity score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
