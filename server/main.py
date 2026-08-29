import os
import sys
import shutil
import hashlib
from typing import List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Setup python path so local_ai and scripts can be imported from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, SessionLocal, KnowledgePack, SyncHistory
from scripts.delta_sync_simulator import (
    get_installed_packs,
    perform_sync,
    delete_local_pack,
    get_pack_local_meta
)
from local_ai.rag_pipeline import query_offline_ai
from local_ai.vector_store import index_file

# Initialize SQLite tables
init_db()

app = FastAPI(title="GyanSetu Local Server & Cloud Simulator")

# Allow CORS for localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global offline state simulation
IS_OFFLINE = False

# Dependency to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic schemas
class InstalledPackInfo(BaseModel):
    id: str
    version: str

class SyncCheckRequest(BaseModel):
    installed_packs: List[InstalledPackInfo]

class SyncLogRequest(BaseModel):
    pack_id: str
    pack_title: str
    status: str # Success, Failed
    size_mb: int
    details: str

class UpdatePackRequest(BaseModel):
    pack_id: str
    new_version: str
    files: List[Dict[str, Any]]

class ChatRequest(BaseModel):
    message: str

class ToggleOfflineRequest(BaseModel):
    offline: bool

# Seed folders
KNOWLEDGE_PACKS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_packs")
DEVICE_STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "device_storage")

os.makedirs(KNOWLEDGE_PACKS_DIR, exist_ok=True)
os.makedirs(DEVICE_STORAGE_DIR, exist_ok=True)

# Helper to write files on cloud
def write_cloud_file(pack_id: str, filename: str, content: str):
    pack_folder = os.path.join(KNOWLEDGE_PACKS_DIR, pack_id)
    os.makedirs(pack_folder, exist_ok=True)
    filepath = os.path.join(pack_folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

# Helper to write files on device
def write_device_file(pack_id: str, filename: str, content: str):
    pack_folder = os.path.join(DEVICE_STORAGE_DIR, pack_id)
    os.makedirs(pack_folder, exist_ok=True)
    filepath = os.path.join(pack_folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

# Knowledge base texts
WHEAT_KARNATAKA_DOC = """Wheat Cultivation Guidelines in Karnataka (Northern Dry & Transition Zones):
• Suitable Agro-Climatic Zones: Zone 3 (Northern Dry Zone) and Zone 8 (Northern Transition Zone), covering Dharwad, Belagavi, Bagalkot, Vijayapura, and Gadag districts.
• Recommended Varieties:
  - Irrigated: UAS-304, DWR-162, GW-322, DWR-2006 (high yield, rust resistant).
  - Rainfed / Dryland: DWR-1006, Bijaga Yellow, A-9-30-1 (durum wheat suited for black soils).
• Sowing Period: Best window is October 15 to November 15. Avoid late sowing after Nov 30 to prevent heat-stress during grain filling.
• Soil & Land Prep: Deep black cotton soils (Vertisols) or clayey loam with pH 6.5–7.8. Ensure fine tilth with 2 ploughings and harrowing.
• Fertilizer (NPK per Hectare):
  - Irrigated: 100 kg N, 50 kg P2O5, 50 kg K2O. Apply 50% N + full P & K at sowing; remaining 50% N at Crown Root Initiation (21-25 days).
  - Rainfed: 50 kg N, 25 kg P2O5, 0 kg K2O as basal dose.
• Critical Irrigation Stages (5-6 waterings):
  1. Crown Root Initiation (CRI): 20–25 days after sowing (most critical).
  2. Tillering Stage: 40–45 days.
  3. Jointing / Stem Elongation: 60–65 days.
  4. Flowering / Heading: 80–85 days.
  5. Grain Milking / Dough Stage: 100–105 days.
• Pest & Disease Management:
  - Rust (Brown/Black): Spray Propiconazole 25 EC @ 1 ml/litre at initial symptom appearance.
  - Termites / Root Grubs: Seed treatment with Chlorpyriphos 20 EC @ 4 ml per kg seed before sowing."""

AGRI_SUBSIDY_DOC = """Agricultural Subsidy and Support Schemes (Karnataka & National):
• PM-KISAN: Direct income support of ₹6,000/year to all eligible landholder farmer families in three 4-monthly installments of ₹2,000.
• Micro-Irrigation Subsidy (Pradhan Mantri Krishi Sinchayee Yojana):
  - 90% government subsidy for Small & Marginal Farmers (< 2 hectares land holding) for drip and sprinkler irrigation installations.
  - 45–55% subsidy for other category farmers.
• Seed & Fertilizer Subsidy (Raitha Siri & NFSM): High-yielding and bio-fortified seeds distributed at 50% subsidy through local Raitha Samparka Kendras (RSK). Nano-urea and bio-fertilizers subsidized up to 50%.
• Farm Mechanization Subsidy: Tractors, power tillers, rotavators, and multi-crop threshers available at 40% to 50% subsidy under Sub-Mission on Agricultural Mechanization (SMAM).
• Mandatory Eligibility Documents: Aadhaar Card, Pahani / RTC land record document, FID (Farmer Registration & Unified Beneficiary Information System), and Aadhaar-linked bank account."""

SOIL_HEALTH_DOC = """Soil Health and Nutrient Management:
• Soil pH Rectification: For acidic soils (pH < 6.0), incorporate agricultural lime (calcium carbonate) @ 2–4 quintals/acre. For alkaline soils (pH > 8.2), apply agricultural gypsum @ 5 quintals/acre along with green manure.
• Organic Matter Enrichment: Apply 10 tonnes of well-decomposed Farm Yard Manure (FYM) or 2 tonnes of vermicompost per hectare 3 weeks before sowing.
• Bio-Fertilizers: Inoculate seed with Azotobacter/Azospirillum (for cereal crops) and Rhizobium (for pulses) @ 250g per 10kg seed to fix atmospheric nitrogen and cut chemical fertilizer usage by 25%."""

PEST_CONTROL_DOC = """Integrated Pest Management & Organic Crop Protection:
• Natural Predators: Conserve ladybird beetles and chrysoperla to biologically control aphids, jassids, and thrips.
• Botanical Sprays: 5% Neem Seed Kernel Extract (NSKE) or Neem oil 1500 ppm @ 3–5 ml/litre acts as a powerful broad-spectrum repellent for chewing and sucking insects.
• Trap Crops: Plant African marigolds as border trap crop around main field to manage root-knot nematodes and fruit borers."""

SCHOLARSHIPS_DOC = """1. National Merit Scholarship: Eligibility: Class 12 passed with >80%, family income < 4.5 LPA. Benefit: ₹10,000/year.\n2. Post-Matric Scholarship for SC/ST: Eligibility: SC/ST students, family income < 2.5 LPA. Benefit: Reimburses full tuition fees."""
FIRST_AID_DOC = """Rural Health Care Guidelines:\n- Heat Stroke: Move patient to cool shade, wipe with cool damp cloth, give ORS if conscious.\n- Snake Bite: Keep victim calm, immobilize bitten limb at or below heart level, clean wound, rush to hospital. Do NOT use tourniquet or suction."""
CURRICULUM_DOC = """Primary Education Standards:\n- Standard 1 Reading: Identify all alphabets, read simple 3-letter words.\n- Standard 1 Math: Addition and subtraction of single digit numbers, recognize shapes."""
LEGAL_DOC = """1. Right to Information (RTI): Any citizen can file request to public authority. Response must be given within 30 days.\n2. Minimum Wages Act: Agricultural workers are entitled to minimum wage set by state authority. Violations can be filed at block office."""

# Seed Cloud Files
write_cloud_file("KP-AGRI-ED-09", "wheat_cultivation_karnataka.txt", WHEAT_KARNATAKA_DOC)
write_cloud_file("KP-AGRI-ED-09", "agricultural_subsidies.txt", AGRI_SUBSIDY_DOC)
write_cloud_file("KP-AGRI-ED-09", "soil_health.txt", SOIL_HEALTH_DOC)
write_cloud_file("KP-AGRI-ED-09", "pest_control.txt", PEST_CONTROL_DOC)

write_cloud_file("KP-SCHOLAR-2024", "scholarships.txt", SCHOLARSHIPS_DOC)
write_cloud_file("KP-HEALTH-RURAL", "first_aid.txt", FIRST_AID_DOC)
write_cloud_file("KP-EDU-PRIMARY", "curriculum.txt", CURRICULUM_DOC)
write_cloud_file("KP-LEGAL-BASIC", "legal_rights.txt", LEGAL_DOC)

# Seed Initial Device Storage
def seed_device_storage():
    import json
    # Scholarship pack installed
    write_device_file("KP-SCHOLAR-2024", "scholarships.txt", SCHOLARSHIPS_DOC)
    scholarship_meta = {
        "id": "KP-SCHOLAR-2024",
        "title": "Government Scholarship Schemes 2024",
        "icon": "account_balance",
        "category": "Education",
        "version": "v2.1",
        "size_mb": 420,
        "files_count": 1,
        "files_metadata": [{"path": "scholarships.txt", "size_bytes": len(SCHOLARSHIPS_DOC), "hash": hashlib.md5(SCHOLARSHIPS_DOC.encode()).hexdigest()}]
    }
    with open(os.path.join(DEVICE_STORAGE_DIR, "KP-SCHOLAR-2024", "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(scholarship_meta, f, indent=2)
    index_file("KP-SCHOLAR-2024", "KP-SCHOLAR-2024/scholarships.txt", SCHOLARSHIPS_DOC)

    # Agriculture pack installed with wheat, subsidies, soil health, pest control
    write_device_file("KP-AGRI-ED-09", "wheat_cultivation_karnataka.txt", WHEAT_KARNATAKA_DOC)
    write_device_file("KP-AGRI-ED-09", "agricultural_subsidies.txt", AGRI_SUBSIDY_DOC)
    write_device_file("KP-AGRI-ED-09", "soil_health.txt", SOIL_HEALTH_DOC)
    write_device_file("KP-AGRI-ED-09", "pest_control.txt", PEST_CONTROL_DOC)
    
    agri_meta = {
        "id": "KP-AGRI-ED-09",
        "title": "Agricultural Best Practices & Crop Data",
        "icon": "agriculture",
        "category": "Agriculture",
        "version": "v1.8",
        "size_mb": 850,
        "files_count": 4,
        "files_metadata": [
            {"path": "wheat_cultivation_karnataka.txt", "size_bytes": len(WHEAT_KARNATAKA_DOC), "hash": hashlib.md5(WHEAT_KARNATAKA_DOC.encode()).hexdigest()},
            {"path": "agricultural_subsidies.txt", "size_bytes": len(AGRI_SUBSIDY_DOC), "hash": hashlib.md5(AGRI_SUBSIDY_DOC.encode()).hexdigest()},
            {"path": "soil_health.txt", "size_bytes": len(SOIL_HEALTH_DOC), "hash": "soil_v18_old"},
            {"path": "pest_control.txt", "size_bytes": len(PEST_CONTROL_DOC), "hash": "pest_v18_old"}
        ]
    }
    with open(os.path.join(DEVICE_STORAGE_DIR, "KP-AGRI-ED-09", "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(agri_meta, f, indent=2)
        
    index_file("KP-AGRI-ED-09", "KP-AGRI-ED-09/wheat_cultivation_karnataka.txt", WHEAT_KARNATAKA_DOC)
    index_file("KP-AGRI-ED-09", "KP-AGRI-ED-09/agricultural_subsidies.txt", AGRI_SUBSIDY_DOC)
    index_file("KP-AGRI-ED-09", "KP-AGRI-ED-09/soil_health.txt", SOIL_HEALTH_DOC)
    index_file("KP-AGRI-ED-09", "KP-AGRI-ED-09/pest_control.txt", PEST_CONTROL_DOC)

# Reseed database & vector store
seed_device_storage()

def check_offline():
    if IS_OFFLINE:
        raise HTTPException(status_code=503, detail="Simulated Offline Mode is enabled. Cannot reach server.")

# ----------------- CLOUD ENDPOINTS -----------------

@app.get("/api/packs")
def list_packs(db: Session = Depends(get_db)):
    check_offline()
    packs = db.query(KnowledgePack).all()
    return packs

@app.get("/api/packs/{pack_id}")
def get_pack(pack_id: str, db: Session = Depends(get_db)):
    check_offline()
    pack = db.query(KnowledgePack).filter(KnowledgePack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Knowledge Pack not found")
    return pack

@app.post("/api/sync/check")
def check_sync(req: SyncCheckRequest, db: Session = Depends(get_db)):
    check_offline()
    updates = []
    installed_map = {item.id: item.version for item in req.installed_packs}
    
    cloud_packs = db.query(KnowledgePack).all()
    for cp in cloud_packs:
        if cp.id in installed_map:
            installed_version = installed_map[cp.id]
            if cp.version != installed_version:
                updates.append({
                    "pack_id": cp.id,
                    "title": cp.title,
                    "icon": cp.icon,
                    "category": cp.category,
                    "server_version": cp.version,
                    "size_mb": cp.size_mb,
                    "files_metadata": cp.files_metadata
                })
    return {"updates": updates}

@app.get("/api/packs/{pack_id}/download/{filename}")
def download_file(pack_id: str, filename: str):
    check_offline()
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    filepath = os.path.join(KNOWLEDGE_PACKS_DIR, pack_id, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found in pack")
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    return {"filename": filename, "content": content}

@app.get("/api/sync/history")
def get_sync_history(db: Session = Depends(get_db)):
    check_offline()
    history = db.query(SyncHistory).order_by(SyncHistory.timestamp.desc()).all()
    formatted = []
    for h in history:
        formatted.append({
            "id": h.id,
            "timestamp": h.timestamp.strftime("%b %d, %H:%M %p"),
            "pack_id": h.pack_id,
            "pack_title": h.pack_title,
            "status": h.status,
            "size_mb": h.size_mb,
            "details": h.details
        })
    return formatted

@app.post("/api/sync/log")
def log_sync(req: SyncLogRequest, db: Session = Depends(get_db)):
    check_offline()
    log = SyncHistory(
        pack_id=req.pack_id,
        pack_title=req.pack_title,
        status=req.status,
        size_mb=req.size_mb,
        details=req.details
    )
    db.add(log)
    db.commit()
    return {"status": "logged", "id": log.id}

# ----------------- LOCAL ON-DEVICE ENDPOINTS -----------------

@app.get("/api/local/status")
def get_local_status(db: Session = Depends(get_db)):
    installed = get_installed_packs()
    pack_sum_mb = sum(p.get("size_mb", 0) for p in installed)
    pack_sum_gb = round(pack_sum_mb / 1000, 1)
    storage_used = 4.2
    
    last_log = db.query(SyncHistory).filter(SyncHistory.status == "Success").order_by(SyncHistory.timestamp.desc()).first()
    last_sync = "2 hours ago"
    if last_log:
        last_sync = last_log.timestamp.strftime("%b %d, %I:%M %p")
        
    return {
        "installed_packs": installed,
        "storage_used_gb": storage_used,
        "storage_total_gb": 16,
        "storage_percent": round((storage_used / 16) * 100, 1),
        "last_sync_time": last_sync,
        "offline_mode": IS_OFFLINE,
        "queries_count": 1248
    }

@app.get("/api/local/offline-state")
def get_offline_state():
    return {"offline": IS_OFFLINE}

@app.post("/api/local/toggle-offline")
def toggle_offline(req: ToggleOfflineRequest):
    global IS_OFFLINE
    IS_OFFLINE = req.offline
    return {"offline": IS_OFFLINE}

@app.post("/api/local/chat")
def local_chat(req: ChatRequest):
    result = query_offline_ai(req.message)
    return result

@app.post("/api/local/sync-pack/{pack_id}")
def local_sync_pack(pack_id: str, db: Session = Depends(get_db)):
    check_offline()
    pack = db.query(KnowledgePack).filter(KnowledgePack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Knowledge Pack not found on server")
        
    result = perform_sync(
        pack_id=pack.id,
        pack_title=pack.title,
        pack_icon=pack.icon,
        pack_category=pack.category,
        server_version=pack.version,
        server_files=pack.files_metadata
    )
    
    log = SyncHistory(
        pack_id=pack.id,
        pack_title=pack.title,
        status="Success",
        size_mb=int(result["bytes_transferred"] / (1024 * 1024)) or 1,
        details=result["details"]
    )
    db.add(log)
    db.commit()
    
    return {
        "status": "success",
        "pack_id": pack_id,
        "files_synced": result["files_synced"],
        "bytes_transferred": result["bytes_transferred"],
        "details": result["details"]
    }

@app.post("/api/local/delete-pack/{pack_id}")
def local_delete_pack(pack_id: str, db: Session = Depends(get_db)):
    delete_local_pack(pack_id)
    return {"status": "success", "pack_id": pack_id}

@app.post("/api/local/clear-space")
def local_clear_space(db: Session = Depends(get_db)):
    db.query(SyncHistory).delete()
    db.commit()
    return {"status": "success", "message": "Cleared storage cache and sync history."}
