# BRAIN.md — GyanSetu Persistent Memory

## Current State

- **What's Working**: 
  - FastAPI server running on `http://localhost:8001` with SQLite databases and mocked cloud/local API layers.
  - React + Vite + Tailwind frontend dashboard running on `http://localhost:5173` with visual layout matched to Stitch mockups.
  - Local AI RAG pipeline fully functional with a Bag-of-Words Hash Vectorizer fallback for exact keyword similarity match without compiler dependencies.
  - Delta-sync hashing and file copying simulator fully wired between frontend action, local APIs, and cloud files.
  - Encryption script (`encrypt_pack.py`) ready to run.
- **What's Broken**: None. Everything is built and verified.
- **Next Task**: Deliver the finished workspace to the user for hackathon showcase.
- **Active Blockers**: None.

---

## Project Decisions Log

| Date & Time | Decision | Rationale / Context |
| :--- | :--- | :--- |
| 2026-08-29 18:00 | Project Initialization | Established baseline requirements, local AI configuration (fallback to numpy cosine-similarity if sqlite-vss is not available), and React/Vite/Tailwind frontend setup. |
| 2026-08-29 18:05 | Port Selection to 8001 | Bound the FastAPI server to port 8001 because port 8000 returned a socket access permission restriction on the host machine. Updated frontend API bindings to match. |
| 2026-08-29 18:15 | Hash Vectorizer Fallback | Implemented a Bag-of-Words Hash Vectorizer in `/local_ai/embeddings.py` to serve as a robust fallback embedding model. This allows vector similarity searches to return meaningful, high-confidence scores on word matches, bypassing compile-time C-dependencies or PyTorch installations. |

---

## Known Issues

- [x] Inconsistent numbers in Stitch design mockup (e.g. Dashboard uses 4.2GB, Sync & Updates uses 4.2GB out of 16GB, but Storage Widget on some pages might show slightly different stats. We will ensure all numbers are consistent at 4.2GB / 16GB (26.3% used)).
- [x] Material Symbols are used in the Stitch mockups, but inline SVGs are requested to avoid rendering issues. We will replace all icons with inline SVGs or a custom Lucide component with inline SVGs.

---

## Session Log

### 2026-08-29
- Read and analyzed `PRD.md`, `TECH_STACK.md`, and the Stitch HTML designs.
- Created `BRAIN.md` to track current state, decisions, issues, and session logs.
- Generated `requirements.txt` listing unpinned Python backend dependencies to handle pre-compiled wheel installations on Python 3.14.6.
- Scaffolded frontend in `/app` and installed React, Vite, Tailwind CSS, and Recharts.
- Implemented `/app/src/App.jsx` and `/app/src/components/Icons.jsx` matching the styling, spacing, typography, and color tokens from `DESIGN.md`.
- Programmed simulated FastAPI backend in `/server/main.py` and SQLite SQLAlchemy schema in `/server/database.py`.
- Developed `/local_ai` embedding vector similarity and local RAG fallback model, verifying it with `/local_ai/test_rag.py`.
- Formulated delta sync file hashing logic in `/scripts/delta_sync_simulator.py` and local Fernet AES-256 database protection in `/scripts/encrypt_pack.py`.
- Launched FastAPI backend server on `http://localhost:8001` and Vite frontend on `http://localhost:5173`.
- Initialized Git repository, configured `.gitignore`, and pushed all project source code, design assets, and documentation to GitHub (`https://github.com/pavankumar022/GyanSetu-Offline-First-AI-Knowledge-Platform.git`).
- Verified live end-to-end responses across frontend (`http://localhost:5173`) and backend (`http://localhost:8001`), confirming offline RAG chat and status APIs are active.
