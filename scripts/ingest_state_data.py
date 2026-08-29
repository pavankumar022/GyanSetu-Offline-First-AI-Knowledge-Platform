"""
ingest_state_data.py
─────────────────────────────────────────────────────────────────────────────
Ingestion pipeline for india_agri_dataset.json

For each of the 36 state/UT records it:
  1. Generates a structured plain-text knowledge document (same style as the
     7 national docs in main.py)
  2. Writes the document to device_storage/KP-AGRI-STATE/<state_slug>.txt
  3. Chunks & embeds it into the local vector store (device_storage/local_knowledge.db)

Called by server/main.py on startup. Safe to call multiple times — existing
entries for the same filepath are deleted first to avoid duplicates.
"""

import os
import sys
import json
import hashlib

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

DATASET_PATH = os.path.join(ROOT_DIR, "india_agri_dataset.json")
DEVICE_STORAGE_DIR = os.path.join(ROOT_DIR, "device_storage")
PACK_ID = "KP-AGRI-STATE"
PACK_DIR = os.path.join(DEVICE_STORAGE_DIR, PACK_ID)

# ── helpers ──────────────────────────────────────────────────────────────────

def slug(name: str) -> str:
    """Convert state name to a safe filename slug."""
    return name.lower().replace(" ", "_").replace("&", "and").replace(",", "")


def _format_list(items: list) -> str:
    """Format a list as a comma-separated string, or 'None recorded' if empty."""
    cleaned = [str(i).strip() for i in items if str(i).strip()]
    return ", ".join(cleaned) if cleaned else "None recorded at state level"


def generate_state_document(record: dict) -> str:
    """
    Generate a structured knowledge document for one state/UT record.

    Mirrors the style of the 7 existing national docs so the same
    hybrid search + LLM fallback pipeline can process them uniformly.

    DATA INTEGRITY: Only data present in the JSON record is written.
    Missing fields are reported as 'Not specified in current knowledge pack'
    rather than filled from general knowledge or guessed.
    """
    name = record["name"]
    kind = record.get("type", "State")
    crops = record.get("major_crops", {})
    kharif = _format_list(crops.get("kharif", []))
    rabi = _format_list(crops.get("rabi", []))
    zaid = _format_list(crops.get("zaid", []))
    livestock = record.get("livestock", "Not specified in current knowledge pack.")
    fisheries = record.get("fisheries", "Not specified in current knowledge pack.")
    gi_products = _format_list(record.get("gi_products", []))

    doc = f"""{name} — State-Level Agriculture, Livestock, Fisheries & GI Products
Source: India State-Level Agriculture Dataset (Ministry of Agriculture, NCERT, CGPDTM GI Registry)
Administrative Type: {kind}
Coverage: State/UT level ONLY. District-level data is NOT available in this knowledge pack.

━━━ MAJOR CROPS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Kharif Season (Sown June–July, Harvested October–November):
  {kharif}

Rabi Season (Sown October–November, Harvested March–April):
  {rabi}

Zaid / Perennial / Plantation Crops:
  {zaid}

━━━ LIVESTOCK ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{livestock}

━━━ FISHERIES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{fisheries}

━━━ GI-TAGGED PRODUCTS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Geographical Indication (GI) registered products from {name}:
  {gi_products}

Note: This lists well-known GI tags verified against the CGPDTM registry.
The full GI list for India has 600+ entries; consult ipindia.gov.in for the
complete current registry.
"""
    return doc.strip()


# ── main ingestion function ──────────────────────────────────────────────────

def ingest_state_dataset() -> dict:
    """
    Load india_agri_dataset.json, generate one document per state/UT,
    write to device_storage, and index into the local vector store.

    Returns a summary dict with counts and file metadata for use by
    the server when updating the KP-AGRI-STATE pack metadata.json.
    """
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    states = data.get("states", [])
    os.makedirs(PACK_DIR, exist_ok=True)

    # Import here to avoid circular dependency if called before server init
    from local_ai.vector_store import index_file, remove_pack_indices, init_store

    # Clear any previously indexed chunks for this pack to avoid duplicates
    init_store()
    remove_pack_indices(PACK_ID)

    files_metadata = []
    generated_docs = {}   # slug -> (filepath, text)

    for record in states:
        state_name = record["name"]
        file_slug = slug(state_name)
        filename = f"{file_slug}.txt"
        filepath_abs = os.path.join(PACK_DIR, filename)
        rel_path = f"{PACK_ID}/{filename}"

        doc_text = generate_state_document(record)
        generated_docs[file_slug] = (rel_path, doc_text)

        # Write to device_storage
        with open(filepath_abs, "w", encoding="utf-8") as f:
            f.write(doc_text)

        # Index into local vector store
        index_file(PACK_ID, rel_path, doc_text)

        files_metadata.append({
            "path": filename,
            "size_bytes": len(doc_text.encode("utf-8")),
            "hash": hashlib.md5(doc_text.encode("utf-8")).hexdigest(),
            "state_name": state_name
        })

    # Write pack metadata.json
    meta = {
        "id": PACK_ID,
        "title": "India State-Level Agriculture, Livestock & GI Products",
        "icon": "map",
        "category": "Agriculture",
        "version": "v1.0",
        "size_mb": round(sum(f["size_bytes"] for f in files_metadata) / (1024 * 1024), 2),
        "files_count": len(files_metadata),
        "files_metadata": files_metadata,
        "description": (
            "State/UT-level data for all 36 Indian states and union territories: "
            "Kharif/Rabi/Zaid crops, livestock specialisation, fisheries focus, "
            "and GI-tagged products. Source: Ministry of Agriculture, CGPDTM GI registry."
        )
    }

    meta_path = os.path.join(PACK_DIR, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    return {
        "records_processed": len(states),
        "pack_id": PACK_ID,
        "files_metadata": files_metadata,
        "meta": meta
    }


# Stand-alone run support
if __name__ == "__main__":
    result = ingest_state_dataset()
    print(f"✅ Ingested {result['records_processed']} state/UT records into pack {result['pack_id']}")
    for f in result["files_metadata"]:
        print(f"   • {f['state_name']} → {f['path']} ({f['size_bytes']} bytes)")
