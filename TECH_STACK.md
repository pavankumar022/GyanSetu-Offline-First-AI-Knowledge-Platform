# Tech Stack — GyanSetu
**100% Local · Zero-Cost · No Cloud Dependencies**

This document is the single source of truth for what technology is used, where, and why. Antigravity should read this before making any architectural changes, and update it if a technology choice changes.

---

## Guiding Constraint

Everything must run on a single laptop with:
```
pip install -r requirements.txt
npm install
```
No AWS, no Firebase, no Vercel, no Docker, no paid API keys, no accounts required to run the project.

---

## 1. Frontend (Web Dashboard)

| Component | Technology | Notes |
|---|---|---|
| Framework | React + Vite | Runs on `localhost:5173` |
| Styling | Tailwind CSS | Design tokens: green `#1B5E20`, off-white `#FAF9F6`, amber `#F5A623` |
| State Management | Zustand or React Context | Lightweight, no Redux needed |
| Charts | Recharts | Storage/sync visualizations |
| Icons | Lucide React (SVG, not icon-font) | Avoids icon-font rendering bugs seen in earlier mockups |

## 2. "Cloud" Server — Simulated Locally

| Component | Technology | Notes |
|---|---|---|
| API Server | FastAPI | Runs on `localhost:8001`, plays the role of "the cloud" |
| Database | SQLite (via SQLAlchemy) | One file, zero setup |
| Knowledge Pack Storage | Local filesystem folder `/knowledge_packs/` | Simulates cloud object storage |

## 3. On-Device / Offline AI Engine (core innovation)

| Component | Technology | Notes |
|---|---|---|
| Local LLM Runtime | `llama-cpp-python` | Runs quantized GGUF models on CPU |
| Model | Phi-3-mini-4k-instruct (Q4_K_M GGUF) or Llama 3.2 1B/3B | Free download from Hugging Face |
| Embedding Model | `sentence-transformers` (all-MiniLM-L6-v2) | Runs locally, no API calls |
| Vector Search | SQLite + `sqlite-vss` (fallback: numpy cosine similarity) | Local `.db` file |
| RAG Pipeline | Custom Python module in `/local_ai/` | Retrieve → rank → prompt → generate |

## 4. Sync & Delta Update System

| Component | Technology | Notes |
|---|---|---|
| Diffing | Content-hash comparison between `/knowledge_packs/` and `/device_storage/` | Simulates real delta-sync |
| "Offline Mode" | Manual UI toggle that bypasses FastAPI and reads directly from `/device_storage/` | Proves offline capability live without needing real Wi-Fi disconnect |

## 5. Security

| Component | Technology | Notes |
|---|---|---|
| Local Encryption | Python `cryptography` library, AES-256 on the local SQLite pack file | Demonstrates the security claim without cloud KMS |
| Transport | Not applicable at demo stage (all localhost) — documented as "would use TLS 1.3 in production" | Roadmap item |

## 6. Version Control

| Component | Technology | Notes |
|---|---|---|
| Source Control | Git + GitHub (public or private repo) | Free, sufficient for hackathon workflow |
| CI/CD | Not used for MVP | Roadmap item if project continues post-hackathon |

---

## 7. Project Folder Structure

```
/gyansetu
  /server            → FastAPI app (simulated cloud), localhost:8001
  /app               → React + Vite + Tailwind dashboard, localhost:5173
  /knowledge_packs   → Source knowledge packs (the "cloud" copy)
  /device_storage    → Downloaded packs (the "on-device" copy)
  /local_ai          → RAG pipeline: embeddings, vector search, local LLM calls
  /scripts           → encrypt_pack.py, delta_sync_simulator.py
  PRD.md
  TECH_STACK.md
  BRAIN.md
  ANTIGRAVITY_PROMPT.md
  README.md
```

---

## 8. Run Commands (for README + demo day)

```bash
# Terminal 1 — start the simulated cloud server
cd server
python -m uvicorn main:app --reload --port 8001

# Terminal 2 — start the frontend dashboard
cd app
npm run dev
```

---

## 9. One-Slide Pitch Deck Summary

```
Frontend Dashboard   → React + Tailwind (localhost)
On-Device AI         → llama.cpp + quantized Phi-3-mini / Llama 3.2 (GGUF)
On-Device Search      → SQLite + Vector Search (sqlite-vss)
"Cloud" Server        → FastAPI + SQLite (runs locally, simulates cloud)
Knowledge Pipeline    → sentence-transformers (chunking + embeddings)
Storage               → Local filesystem (simulates cloud storage)
Sync                  → Delta-update via content hashing
Security              → AES-256 local encryption
Cost                  → ₹0 — fully open-source, runs on one laptop
```

---

## 10. Living Document Notice

This file must be updated by Antigravity whenever a technology choice changes (e.g. swapping the local LLM model, adding a new library). Log the change in `BRAIN.md` as well.
