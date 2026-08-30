# BRAIN.md — GyanSetu Persistent Memory

## Current State

- **What's Working**: 
  - FastAPI server running on `http://localhost:8001` with SQLite databases and mocked cloud/local API layers.
  - React + Vite + Tailwind frontend dashboard running on `http://localhost:5173` with visual layout matched to Stitch mockups.
  - Local AI RAG engine (v4.0) with Intent-Aware Retrieval, Sub-Topic Tagging, Dedicated-Document Boosting, and 75% Confidence Guardrail (**100% benchmark pass rate** across 35 novel test cases in `scripts/eval_rag.py`).
  - Knowledge Base expanded across 7 complete categories (28 major Indian crops, national & Karnataka schemes, rural health SOPs, organic/IPM soil management, and legal rights — 89 total files, 718 indexed chunks).
  - Delta-sync hashing and file copying simulator fully wired between frontend action, local APIs, and cloud files.
  - Encryption script (`encrypt_pack.py`) ready to run.
- **What's Broken**: None. Everything is built, expanded, and verified.
- **Next Task**: Deliver the finished workspace to the user for hackathon showcase.
- **Active Blockers**: None.

---

## Project Decisions Log

| Date & Time | Decision | Rationale / Context |
| :--- | :--- | :--- |
| 2026-08-29 18:00 | Project Initialization | Established baseline requirements, local AI configuration (fallback to numpy cosine-similarity if sqlite-vss is not available), and React/Vite/Tailwind frontend setup. |
| 2026-08-29 18:05 | Port Selection to 8001 | Bound the FastAPI server to port 8001 because port 8000 returned a socket access permission restriction on the host machine. Updated frontend API bindings to match. |
| 2026-08-29 18:15 | Hash Vectorizer Fallback | Implemented a Bag-of-Words Hash Vectorizer in `/local_ai/embeddings.py` to serve as a robust fallback embedding model. This allows vector similarity searches to return meaningful, high-confidence scores on word matches, bypassing compile-time C-dependencies or PyTorch installations. |
| 2026-08-30 08:35 | 75% RAG Confidence Threshold & Crop Context Chunking | Enforced a strict 75% similarity confidence threshold in `/local_ai/rag_pipeline.py`. Queries scoring below 75% return a grounded fallback message without citation chips. Prepended document titles to every chunk header and added crop-alias alignment to eliminate wrong-document cross-retrieval. |
| 2026-08-30 09:10 | Sub-Topic Tagging & Intent-Aware Answer Generation | Added `_SUBTOPIC_RULES` at index time to tag chunks with sub-topics (irrigation, fertilizer, sowing, spacing, varieties, pest, disease, yield, soil, eligibility, cost, health-protocol, legal-rights) and `_INTENT_KEYWORD_MAP` at query time. Applied a +0.20 sub-topic boost and a +0.25 dedicated-document specificity boost in `search_chunks`. Rewrote `llm_client.py` with sub-topic sentence extraction to prevent cross-topic answer bleed. |
| 2026-08-30 09:15 | 7-Category Comprehensive Knowledge Expansion | Expanded knowledge base across 7 categories (28 major Indian crops, 10 government schemes, 6 rural health SOPs, 4 soil/IPM guides, 4 legal rights documents — 89 total files, 718 chunks). Re-indexed vector DB and verified with `scripts/eval_rag.py` (35/35 tests passing, **100% score**). |

---

## Known Issues

- [x] Inconsistent numbers in Stitch design mockup (e.g. Dashboard uses 4.2GB, Sync & Updates uses 4.2GB out of 16GB). Standardized at 4.2GB / 16GB (26.3% used).
- [x] Material Symbols replaced with Lucide React SVG components across all frontend screens to prevent icon-font rendering issues.
- [x] Wrong document retrieval on crop queries (e.g. "corn growing suitable fertilizer"). Resolved by prepending crop context to headers, adding sub-topic tagging, dedicated-document boosting, and expanding crop documents.
- [x] Sub-topic answer bleed (e.g. returning pest info when irrigation was asked). Resolved by implementing sub-topic sentence relevance scoring in `llm_client.py` and dedicated-document boosting in `vector_store.py`. Validated against `scripts/eval_rag.py` harness with 35 novel question phrasings (**100% pass rate**).

---

## Session Log

### 2026-08-29
- Read and analyzed `PRD.md`, `TECH_STACK.md`, and the Stitch HTML designs.
- Created `BRAIN.md` to track current state, decisions, issues, and session logs.
- Generated `requirements.txt` listing unpinned Python backend dependencies to handle pre-compiled wheel installations on Python 3.14.6.
- Scaffolded frontend in `/app` and installed React, Vite, Tailwind CSS, and Recharts.
- Implemented `/app/src/App.jsx` and `/app/src/components/Icons.jsx` matching styling tokens.
- Programmed simulated FastAPI backend in `/server/main.py` and SQLite SQLAlchemy schema in `/server/database.py`.
- Developed `/local_ai` embedding vector similarity and local RAG fallback model.
- Formulated delta sync file hashing logic in `/scripts/delta_sync_simulator.py` and Fernet AES-256 protection in `/scripts/encrypt_pack.py`.
- Launched FastAPI backend server on `http://localhost:8001` and Vite frontend on `http://localhost:5173`.
- Initialized Git repository and pushed all source code to GitHub (`https://github.com/pavankumar022/GyanSetu-Offline-First-AI-Knowledge-Platform.git`).

### 2026-08-30
- Fixed wrong-document retrieval bug by prepending document titles to chunk section labels, adding `_CROP_ALIASES` and cross-crop match score capping in `search_chunks`, and enforcing a 75% confidence threshold with citation-free fallback responses in `query_offline_ai`.
- Expanded knowledge pack with 8 initial crop documents (`maize`, `rice`, `ragi`, `sugarcane`, `cotton`, `groundnut`, `pigeon_pea`, `sunflower`).
- Implemented Intent-Aware Retrieval & Answer Generation: sub-topic tagging at index time (`_SUBTOPIC_RULES`), intent-keyword lookup at query time (`_INTENT_KEYWORD_MAP`), sub-topic boosting (+0.20), and dedicated-document specificity boosting (+0.25) in `vector_store.py`.
- Rewrote `llm_client.py` with sub-topic sentence relevance scoring (`_sentence_relevance` with 0.3 bonus per sub-topic hit) to ensure answers strictly address the specific sub-topic asked without cross-topic bleed.
- Executed comprehensive 7-category knowledge base expansion pass: added 20+ new structured documents across Cereals, Pulses, Oilseeds, Cash Crops, Fruits, Vegetables, Plantation Crops, Government Schemes (Raitha Siri, Bhoochetana, e-NAM), Rural Health (Child Malnutrition, AMB, POSHAN), and Legal Rights (Agri Input Consumer Rights).
- Updated `metadata.json` for all packs to `v4.0` (89 total files indexed, 718 chunks).
- Created `KNOWLEDGE_COVERAGE.md` v4.0 documenting all 28 crops, 10 schemes, 6 health SOPs, 4 soil/IPM guides, and 4 legal rights documents.
- Created and executed `scripts/eval_rag.py` evaluation harness: verified 35 novel question phrasings across all 7 categories (**35/35 passed — 100% score**).
