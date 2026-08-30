"""
reindex_all.py — Drop and rebuild GyanSetu vector DB with the new semantic chunker.

Run from project root:
    python scripts/reindex_all.py
"""

import os
import sys
import sqlite3
import time

# ── Path setup so local_ai imports work ──────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from local_ai.vector_store import init_store, index_file, DB_PATH, chunk_text
from local_ai.embeddings import get_embedding

DEVICE_STORAGE = os.path.join(PROJECT_ROOT, "device_storage")
PACK_IDS = {
    "KP-AGRI-ED-09": "KP-AGRI-ED-09",
    "KP-AGRI-STATE": "KP-AGRI-STATE",
    "KP-HEALTH-RURAL": "KP-HEALTH-RURAL",
    "KP-LEGAL-BASIC": "KP-LEGAL-BASIC",
    "KP-SCHOLAR-2024": "KP-SCHOLAR-2024",
}

# ── Validation queries for before/after scoring ───────────────────────────────
TEST_QUERIES = [
    ("paddy transplant days", ["transplant", "25 days", "nursery"]),
    ("NPK dose irrigated wheat Punjab", ["120", "60", "40"]),
    ("AWD alternate wetting drying rice", ["awd", "wetting"]),
    ("PM-KISAN benefit eligibility", ["6,000", "kisan"]),
    ("best time plant coffee vietnam", []),  # should score very low (out of scope)
]


def count_chunks():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM knowledge_chunks")
        n = cur.fetchone()[0]
    except Exception:
        n = 0
    conn.close()
    return n


def drop_all_chunks():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM knowledge_chunks")
    conn.commit()
    conn.close()


def score_query(query: str):
    """Return the top cosine similarity for a query against the current index."""
    from local_ai.vector_store import search_chunks
    results = search_chunks(query, top_k=1)
    if results:
        return results[0]["base_score"], results[0]["text"][:80]
    return 0.0, ""


def main():
    print("=" * 70)
    print("  GyanSetu — Vector DB Re-Indexer (Semantic Chunker)")
    print("=" * 70)

    init_store()

    # ── BEFORE stats ─────────────────────────────────────────────────────────
    before_count = count_chunks()
    print(f"\n[BEFORE] Chunk count in DB: {before_count}")

    print("\n[BEFORE] Top retrieval scores for test queries:")
    before_scores = {}
    for query, _ in TEST_QUERIES:
        score, excerpt = score_query(query)
        before_scores[query] = score
        print(f"  {score:.4f}  Q: {query:<45}  | {excerpt}...")

    # ── Drop old chunks ───────────────────────────────────────────────────────
    print(f"\nDropping all {before_count} old chunks...")
    drop_all_chunks()
    print("Done.")

    # ── Re-index every pack ───────────────────────────────────────────────────
    total_files = 0
    total_chunks = 0

    for pack_dir, pack_id in PACK_IDS.items():
        pack_path = os.path.join(DEVICE_STORAGE, pack_dir)
        if not os.path.isdir(pack_path):
            print(f"  [SKIP] Pack directory not found: {pack_path}")
            continue

        txt_files = [f for f in os.listdir(pack_path) if f.endswith(".txt")]
        print(f"\n[{pack_id}] Indexing {len(txt_files)} files...")

        for fname in txt_files:
            fpath = os.path.join(pack_path, fname)
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Show chunk preview for this file
            source_label = os.path.splitext(fname)[0].replace("_", " ").replace("-", " ").title()
            chunks_preview = chunk_text(content, source_label=source_label)
            print(f"  {fname:<50}  -> {len(chunks_preview)} chunks")

            t0 = time.time()
            index_file(pack_id, fpath, content)
            elapsed = time.time() - t0

            total_files += 1
            total_chunks += len(chunks_preview)

    # ── AFTER stats ───────────────────────────────────────────────────────────
    after_count = count_chunks()
    print(f"\n[AFTER] Chunk count in DB: {after_count}  (was {before_count})")
    print(f"        Files indexed: {total_files}")
    print(f"        Average chunks/file: {total_chunks / max(total_files, 1):.1f}")

    print("\n[AFTER] Top retrieval scores for test queries:")
    for query, expected_kws in TEST_QUERIES:
        score, excerpt = score_query(query)
        before = before_scores.get(query, 0.0)
        delta = score - before
        delta_str = f"({'+' if delta >= 0 else ''}{delta:.4f})"
        hit = "[OK]" if score > 0.15 or not expected_kws else "[FAIL]"
        if not expected_kws:
            # Out-of-scope should be LOW
            hit = "[OK]" if score < 0.20 else "[WARN] (may be too high for out-of-scope)"
        print(f"  {hit:<6} {score:.4f} {delta_str}  Q: {query:<45}  | {excerpt}...")

    print("\n" + "=" * 70)
    print("  Re-indexing complete!")
    print("  Restart the uvicorn server to pick up the new chunks.")
    print("=" * 70)


if __name__ == "__main__":
    main()
