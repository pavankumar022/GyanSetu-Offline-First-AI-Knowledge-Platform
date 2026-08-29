# Product Requirements Document (PRD)
## GyanSetu — Offline-First AI Knowledge Platform
**Smart India Hackathon — Selection Round**

---

## 1. Problem Statement

Millions of people in rural, remote, and low-connectivity regions of India — farmers, students, healthcare workers, government field staff — need access to trusted, verified information but cannot rely on continuous internet access.

Existing AI assistants fail the moment connectivity drops — exactly when field-level users need answers most.

> **Core Problem:** Trusted AI-powered answers should not require a live internet connection every single time a question is asked.

---

## 2. Proposed Solution

An **Offline-First AI Knowledge Platform** that:

1. Downloads curated, trusted "Knowledge Packs" (government manuals, agricultural advisories, health guidelines) while internet is available.
2. Stores this knowledge securely and locally on-device.
3. Uses a **local AI model + on-device search (RAG)** to answer user questions **completely offline**.
4. Syncs only *changed* portions of knowledge (delta updates) when internet returns.

**One-line pitch:** *Download trusted knowledge once → store it locally → use AI locally → update when internet returns.*

---

## 3. Target Users

| User Segment | Use Case |
|---|---|
| Farmers (rural/remote areas) | Crop advisory, fertilizer recommendations, pest control |
| Students in low-connectivity regions | Offline syllabus material, exam prep Q&A |
| ASHA / healthcare field workers | Offline treatment protocols, maternal health guidelines |
| Government field staff | Scheme eligibility, procedural manuals |

---

## 4. Core System Components

| Component | Function |
|---|---|
| **"Cloud" Server (simulated locally)** | Ingests trusted documents, prepares downloadable Knowledge Packs |
| **App & Local Storage** | Lets users select/download knowledge domains; stores them locally |
| **Offline AI Question-Answering Engine** | On-device vector search + local LLM (RAG) answers questions offline |
| **Sync Engine** | Checks for updates; downloads only the delta (changed data) |

---

## 5. User Flow

```
Trusted Documents
      ↓
Prepare & Organize into Knowledge Packs (Local "Server" Process)
      ↓
User Downloads Relevant Pack (App)
      ↓
User Asks a Question (Offline Mode)
      ↓
On-Device Search (Local Vector DB) finds relevant chunks
      ↓
Local AI Model generates grounded answer
      ↓
Answer shown to User — with source citation
      ↓
(When "online") → Check for Updates → Download only Delta → Update Local Knowledge
```

---

## 6. Key Differentiator vs. Normal Cloud AI

| Normal Cloud AI | GyanSetu (Offline-First) | Why It Matters |
|---|---|---|
| Needs continuous internet | Works fully offline after initial download | Usable in remote/low-connectivity areas |
| Query sent to remote server | Query processed on-device | Zero latency dependency, better privacy |
| Generic/open internet knowledge | Curated, pre-approved trusted sources | Reduces misinformation, domain-accurate |
| Server handles all updates | Lightweight delta-sync | Saves bandwidth/cost |

---

## 7. Architecture Decision: 100% Local, Zero-Cost Demo

**Decision:** For the hackathon build, the entire system runs locally on a laptop — no AWS, no Firebase, no Vercel, no Docker, no paid API keys. See `TECH_STACK.md` for full detail.

- The "cloud server" is simulated as a second local process (FastAPI on `localhost:8000`).
- "Downloading a pack" simulates by copying files from a local `/knowledge_packs` folder into a local `/device_storage` folder.
- A manual "Simulate Offline" toggle in the UI proves offline capability live on stage without needing to physically disconnect the internet.
- This keeps the project fully reproducible, free, and demo-safe (no dependency on live Wi-Fi/venue internet during judging).

---

## 8. MVP Scope for Hackathon Demo

1. ✅ One domain for demo: **Agriculture advisory**
2. ✅ Pre-packaged Knowledge Pack (2–3 official PDFs → chunked → embedded, stored locally)
3. ✅ Working offline RAG pipeline demoed via the "Simulate Offline" toggle
4. ✅ Delta-sync demo: simulate an update in the local server folder → show app downloading only the small diff
5. ✅ Source citation shown with every answer
6. ✅ Dashboard, Chat, Knowledge Packs, Sync, Settings screens (see Stitch designs)

**Out of scope for MVP:** multi-language UI (mentioned only as roadmap), real cloud hosting, user accounts/auth, mobile app store deployment.

---

## 9. Known Limitations / Risks & Mitigations

| Risk | Mitigation |
|---|---|
| How much knowledge fits locally? | Quantized models + efficient chunking; scope by domain-specific packs |
| Local AI speed on low-end devices | Small quantized models (1B–3B params); benchmark on demo laptop |
| Answer accuracy / hallucination | RAG grounding + citation display + "I don't have this information" fallback |
| Question outside downloaded knowledge | Explicit "out of scope" response instead of guessing |
| Judges question "is this really offline?" | Live "Simulate Offline" toggle + optional real Wi-Fi-off demo |

---

## 10. Impact & Alignment with SIH Themes

- Digital India / Rural Empowerment — brings AI to connectivity-deprived regions.
- Reduces digital divide — no dependency on continuous data/internet cost.
- Trust & Governance — uses only verified/government-approved sources.
- Scalable — same architecture applies across agriculture, health, education, disaster management.
- Cost-efficient — delta updates reduce data costs; entire dev stack is free/open-source.

---

## 11. 60-Second Pitch

> "Our platform is an AI system designed to work even when the internet is unavailable. We collect trusted documents — like government manuals and official advisories — and convert them into downloadable Knowledge Packs. Users download them once. After that, they can ask questions entirely offline: the device searches its stored knowledge and a local AI model generates a grounded, cited answer — no internet required. When connectivity returns, the app checks for updates and downloads only what has changed. In short: download trusted knowledge once, store it locally, use AI locally, and update whenever connectivity returns."

---

## 12. Roadmap (Post-Hackathon / Future Scope)

- Multi-language UI: Hindi, Kannada, and other regional languages
- Real cloud hosting (AWS/GCP) for production-scale Knowledge Pack distribution
- Mobile app (Flutter) with app store deployment
- Multi-domain packs (health, education, disaster management)
- User accounts, analytics dashboard, admin panel for content curation

---

## 13. Living Document Notice

This PRD is a **living document** — Antigravity (or any assistant continuing this project) has permission to update it as the project evolves. See `BRAIN.md` for the current live project state and `ANTIGRAVITY_PROMPT.md` for build instructions.

*Last updated: see BRAIN.md → "Last Updated" field for the current timestamp.*
