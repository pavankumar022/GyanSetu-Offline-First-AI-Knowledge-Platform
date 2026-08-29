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

# ============================================================
# NATIONAL KNOWLEDGE BASE — India-wide coverage, all zones
# Source: ICAR, National Food Security Mission, Ministry of Agriculture
# ============================================================

WHEAT_INDIA_DOC = """Wheat Cultivation — National Advisory (All Wheat-Growing States of India)
Source: ICAR-Indian Institute of Wheat and Barley Research (IIWBR), Karnal; NFSM-Wheat

Major Wheat-Growing States (Rabi Crop — Kharif Season NOT suitable for wheat):
• Top Producers (Area/Production): Uttar Pradesh, Punjab, Haryana, Madhya Pradesh, Rajasthan, Bihar, Gujarat, Uttarakhand.
• Secondary Producers: Himachal Pradesh, Jammu & Kashmir, Maharashtra (Northern dry zones), Karnataka (Zones 3 & 8 only).
• NOT Recommended for Wheat Cultivation: Coastal regions (Mumbai, Goa, Kerala, Tamil Nadu coast) — high humidity and warm winters prevent proper vernalization.

Recommended Varieties by State/Zone:
• Punjab / Haryana (Irrigated — High Input):
  - PBW-1 Chapati (HD-2967), DBW-222 (WB02), HD-3086, WH-1105. Sowing: Nov 1–20. Yield: 55–65 q/ha.
• Uttar Pradesh (Western — Irrigated):
  - HD-2967, GW-496, DBW-187, WH-711. Sowing: Oct 25 – Nov 20. Yield: 50–60 q/ha.
• Uttar Pradesh (Eastern — Rainfed / Late-sown):
  - HI-8498, NW-1014, K-307, Raj-4120. Sowing: Dec 1–20 (late-sown tolerant varieties). Yield: 30–40 q/ha.
• Madhya Pradesh / Rajasthan (Central Zone):
  - HI-8498 (Durum/Hard wheat), GW-322, JW-3288, MP-3336. Sowing: Nov 10–Dec 5. Yield: 35–50 q/ha.
• Karnataka (Northern Dry Zones 3 & 8 — Dharwad, Belagavi, Bagalkot, Vijayapura, Gadag):
  - Irrigated: UAS-304, DWR-162, GW-322, DWR-2006. Rainfed: DWR-1006, Bijaga Yellow. Sowing: Oct 15 – Nov 15. Yield: 30–45 q/ha.
• Bihar / Jharkhand (Eastern Zone):
  - HD-2781, PBW-343, K-0307, DBW-14. Sowing: Nov 10–30. Yield: 35–45 q/ha.

Fertilizer Recommendations (NPK — kg/ha):
• Irrigated (5–6 waterings): 120 kg N : 60 kg P2O5 : 40 kg K2O. Apply 50% N at sowing + 50% N at CRI (25 days).
• Rainfed / Limited Irrigation (1–2 waterings): 60 kg N : 30 kg P2O5 : 20 kg K2O — full dose as basal.
• Late-sown (December): 80 kg N : 40 kg P2O5 : 30 kg K2O with top-dressing post-CRI.

Critical Irrigation Stages (Priority order if only limited water available):
1. Crown Root Initiation (CRI): 20–25 DAS — MOST CRITICAL, skip only in emergency.
2. Tillering: 40–45 DAS.
3. Jointing / Stem Elongation: 60–65 DAS.
4. Boot Stage / Heading: 80–85 DAS.
5. Dough / Grain Milking: 100–105 DAS.

Pest & Disease Management:
• Wheat Rust (Brown/Yellow/Black): Spray Propiconazole 25 EC @ 1 ml/L or Tebuconazole 250 EW @ 1 ml/L at first sign. Repeat at 15-day interval.
• Aphids: Apply Thiamethoxam 25 WG @ 100g/ha or Imidacloprid 17.8 SL @ 150 ml/ha when >15 aphids/tiller appear.
• Termites / Root Grubs: Seed treatment with Chlorpyriphos 20 EC @ 4 ml/kg seed before sowing.
• Yellow Mosaic Virus (Barley Yellow Dwarf): Use certified disease-free seed; control aphid vector as above."""

RICE_INDIA_DOC = """Rice (Paddy) Cultivation — National Advisory
Source: ICAR-National Rice Research Institute (NRRI), Cuttack; Directorate of Rice Development (DRD)

Major Rice-Growing States:
• Kharif (Monsoon — June to November): West Bengal, Uttar Pradesh, Punjab, Andhra Pradesh, Telangana, Tamil Nadu, Odisha, Bihar, Chhattisgarh, Maharashtra, Assam.
• Rabi / Summer Rice: West Bengal (Boro), Odisha, Kerala backwater areas.

Recommended Varieties by Region:
• Punjab / Haryana (Irrigated Kharif):
  - Pusa-44 (high yield — AVOID, long duration), PR-126, PR-121, PB-1509 (Basmati). Transplant: June 10–30 (after paddy nursery 25 days). Yield: 60–70 q/ha.
• Uttar Pradesh:
  - Swarna (MTU-7029), Sarjoo-52, NDR-359. Transplant: July 10–Aug 15.
• West Bengal / Odisha / Bihar:
  - Swarna Sub1 (flood-tolerant), Sambha Mahsuri, Lalat, IR-64. Yield: 40–55 q/ha.
• Andhra Pradesh / Telangana:
  - MTU-1010, BPT-5204 (Sona Masuri), NLR-34449. Yield: 50–65 q/ha.
• Assam / North-East (Hill Rice):
  - Joha (aromatic — local special), Disang, Ranjit. Direct-seeded in hill terraces.

Fertilizer (NPK — kg/ha for irrigated rice):
• Transplanted: 120 kg N : 60 kg P2O5 : 60 kg K2O. Split N: 1/3 at transplanting, 1/3 at active tillering (25-30 DAT), 1/3 at panicle initiation.
• Direct-Seeded: 100 kg N : 50 kg P2O5 : 50 kg K2O.

Water Management:
• Maintain 2–5 cm standing water during tillering to panicle initiation.
• Drain 10 days before harvest. Alternate Wetting and Drying (AWD) can save 20–30% water while maintaining yield."""

PULSES_INDIA_DOC = """Pulses — National Advisory (Tur/Pigeon Pea, Gram, Moong, Urad)
Source: ICAR-Indian Institute of Pulses Research (IIPR), Kanpur

1. Pigeon Pea (Tur / Arhar) — Kharif Crop:
• Recommended States: Maharashtra, Karnataka, Andhra Pradesh, Madhya Pradesh, Uttar Pradesh, Gujarat.
• Varieties: ICPH-2671 (short duration), Maruti, BDN-711, BSMR-736, TJT-501.
• Sowing: June 15 – July 15 (with onset of monsoon). Row spacing: 60 cm x 20 cm.
• Fertilizer: 20 kg N + 50 kg P2O5 at sowing (Rhizobium seed inoculation reduces N requirement).
• Harvest: 150–180 days (medium-early varieties at 100–120 days).

2. Chickpea (Gram / Chana) — Rabi Crop:
• Recommended States: Madhya Pradesh, Rajasthan, Maharashtra, Uttar Pradesh, Andhra Pradesh, Karnataka.
• Varieties: JG-11 (Desi), JG-16, KAK-2 (large-seeded Kabuli), JAKI-9218.
• Sowing: October 20 – November 20. Avoid late sowing — increases root rot and wilt risk.
• Fertilizer: 20 kg N + 40 kg P2O5 at sowing. Rhizobium + PSB seed treatment recommended.
• Wilt Management: Seed treatment with Trichoderma viride @ 4g/kg + Carbendazim @ 2g/kg seed.

3. Green Gram (Moong) — Kharif or Summer:
• Recommended States: Rajasthan, Maharashtra, Andhra Pradesh, Karnataka, Odisha.
• Varieties: IPM-02-03, Pusa-Vishal, KM-2241, SML-668.
• Sowing (Kharif): June – July. Sowing (Spring/Summer): March – April.
• Fertilizer: 20 kg N + 40 kg P2O5 at sowing."""

AGRI_SUBSIDY_DOC = """Agricultural Subsidy and Support Schemes — National (All India)
Source: Ministry of Agriculture & Farmers' Welfare, Government of India

1. PM-KISAN (Pradhan Mantri Kisan Samman Nidhi):
• Benefit: Direct income support of ₹6,000/year in three equal installments of ₹2,000 every 4 months.
• Eligibility: All landholder farmer families (small, marginal, and medium) with cultivable land.
• Exclusions: Institutional landholders; farmers who are/were constitutional post holders; serving/retired govt. employees drawing pension > ₹10,000/month; income-tax payers.
• How to Apply: Visit nearest Common Service Centre (CSC) or PM-KISAN portal (pmkisan.gov.in) with Aadhaar, land record (Khata/Pahani/RTC), and Aadhaar-linked bank account.

2. PM-KISAN Maandhan (PM Kisan Pension Yojana):
• Benefit: ₹3,000/month pension at age 60.
• Eligibility: Small & Marginal Farmers aged 18–40 years with landholding up to 2 ha.
• Contribution: ₹55–₹200/month (age-based sliding scale) matched equally by government.

3. Pradhan Mantri Fasal Bima Yojana (PMFBY — Crop Insurance):
• Coverage: All food crops (cereal, millets, pulses), oilseeds, annual commercial/horticultural crops.
• Premium: 2% of sum insured for Kharif crops; 1.5% for Rabi crops; 5% for annual horticultural crops.
• Sum Insured: Based on Scale of Finance (district-level threshold yield). Government pays remaining premium.
• Coverage Events: Natural calamities (drought, flood, hailstorm, cyclone), pest/disease outbreaks, prevented sowing.
• How to Apply: Through bank at time of crop loan sanction, or via CSC/insurance company agent.

4. Pradhan Mantri Krishi Sinchayee Yojana (PMKSY — Micro-Irrigation):
• Subsidy: 90% for Small & Marginal Farmers (< 2 ha) for drip and sprinkler systems; 45–55% for others.
• State Implementation: Apply through state Agriculture Department; physical verification required before installation.

5. National Food Security Mission (NFSM):
• Purpose: Technology dissemination; certified seed distribution at 50% subsidy.
• Crops Covered: Rice, wheat, pulses, coarse cereals, oilseeds.
• State Distribution: Through Raitha Samparka Kendra (Karnataka), Krishi Vigyan Kendra (KVK), block-level agriculture offices.

6. Sub-Mission on Agricultural Mechanization (SMAM):
• Subsidy: 40–50% for tractors, power tillers, rotavators, combine harvesters, seed drills, threshers.
• Special Provision: Women farmers and SC/ST farmers get 10% additional subsidy.

Required Documents for Most Schemes: Aadhaar Card, Land Record (Pahani/Khata/7-12 extract), Bank Passbook copy (Aadhaar-linked), Farmer Registration (eKYC on PM-KISAN portal)."""

SOIL_HEALTH_DOC = """Soil Health and Nutrient Management — National Advisory
Source: ICAR-National Bureau of Soil Survey & Land Use Planning (NBSS&LUP); Ministry of Agriculture Soil Health Card scheme

Soil Health Card (SHC) Scheme:
• Purpose: Government provides free soil testing every 2 years through Soil Testing Labs (STLs). Card recommends precise NPK and micronutrient doses.
• How to get: Contact nearest agriculture office/KVK. Collect soil sample from 0–20 cm depth from 5 spots in the field. Mix and submit ~500g composite sample.

pH Management by Region:
• Acidic Soils (pH < 6.0) — Common in North-East India, Kerala, West Bengal, Assam:
  - Apply Agricultural Lime (CaCO3) @ 2–4 quintals/acre. Incorporate 3 weeks before sowing.
  - Use lime-tolerant crops: rice, maize, sugarcane.
• Alkaline / Saline Soils (pH > 8.2) — Common in Punjab, Haryana, Rajasthan, UP (usar lands):
  - Apply Gypsum (CaSO4) @ 5 quintals/acre before first ploughing.
  - Grow salt-tolerant crops first: barley, sugarbeet, dhaincha (green manure).
• Neutral / Loam (pH 6.5–7.5): Optimum. Most crops perform best. Maintain with organic matter.

Organic Matter Improvement (All States):
• Apply 8–10 tonnes of well-decomposed Farm Yard Manure (FYM) per hectare or 2 tonnes vermicompost 3 weeks before sowing.
• Green Manuring: Grow Dhaincha (Sesbania bispinosa) or Sun hemp and incorporate at 40–45 days — adds 80–120 kg N/ha.

Micronutrient Deficiency Corrections:
• Zinc Deficiency (Most common — affects rice, wheat, maize in Punjab, Haryana, UP, Bihar, Karnataka):
  - Apply Zinc Sulphate (ZnSO4) 21% @ 25 kg/ha to deficient soils. Foliar spray 0.5% ZnSO4 + 0.25% slaked lime at tillering.
• Boron Deficiency (Sunflower, groundnut, cauliflower in South India):
  - Apply Borax @ 1.5 kg/ha as basal dose.
• Iron Deficiency (Calcareous soils of Rajasthan, UP):
  - Spray FeSO4 @ 0.5% at active growth stage."""

PEST_CONTROL_DOC = """Integrated Pest Management (IPM) — National Advisory
Source: National Centre for Integrated Pest Management (NCIPM), New Delhi; ICAR

IPM Principles (Prefer in order listed below — chemical pesticide is LAST resort):
1. Cultural Controls (Preventive — No cost):
   • Crop rotation (break pest cycle: alternate cereals with pulses/oilseeds).
   • Resistant/tolerant varieties (e.g. BPT-5204 rice resists stem borer; Swarna Sub1 tolerates flood stress).
   • Deep summer ploughing: Exposes soil-borne pests and pupae to sun/birds. Do every 2–3 years.
   • Destruction of crop stubble/residue immediately after harvest.

2. Biological Controls (Eco-friendly):
   • Conserve natural predators: Ladybird beetles, Chrysoperla (green lacewing), Spiders — these control aphids, jassids, thrips.
   • Release Trichogramma cards (egg parasitoid) @ 1 lakh/acre at egg-laying stage — controls bollworm, stem borer, army worm.
   • Apply Beauveria bassiana or Metarhizium anisopliae (entomopathogenic fungi) for soil-dwelling pests.
   • Use Nuclear Polyhedrosis Virus (NPV) for Helicoverpa armigera (cotton bollworm, tomato fruit borer).

3. Botanical / Biopesticides:
   • 5% Neem Seed Kernel Extract (NSKE): Spray 5 kg kernels extracted in 10L water per acre. Controls aphids, whitefly, jassids.
   • Neem oil 1500 ppm @ 3–5 ml/L: Broad-spectrum repellent.
   • Garlic extract 5%: Fungicidal and repellent spray.

4. Physical / Mechanical Controls:
   • Yellow Sticky Traps: 10–15 per acre for whitefly and aphid monitoring and mass trapping.
   • Pheromone Traps: 5 traps/acre for Spodoptera, Helicoverpa, pink bollworm monitoring.
   • Light Traps: 1 trap per 5 acres for moth monitoring and mass capture (switch on 7 PM – 10 PM).

5. Chemical Pesticide Use (Only as last resort when Economic Threshold Level crossed):
   • Always use recommended dose — never exceed label rate.
   • Wear PPE (gloves, mask, boots) during spraying.
   • Observe Pre-Harvest Interval (PHI) strictly before harvesting crop.
   • Do NOT spray during flowering — protects pollinators."""

SCHOLARSHIPS_DOC = """Government Scholarship Schemes — National (All India)
Source: National Scholarship Portal (scholarships.gov.in); Ministry of Education; Ministry of Tribal Affairs

1. National Means-cum-Merit Scholarship (NMMSS):
   Eligibility: Class 8 students, family income < ₹3.5 lakh/year, 55% marks in Class 7.
   Benefit: ₹12,000/year (₹1,000/month) for Class 9–12. Apply: Through state government by state nomination.

2. Pre-Matric Scholarship for Minorities (Class 1–10):
   Eligibility: Minority community students (Muslim, Christian, Sikh, Buddhist, Parsi, Jain), family income < ₹1 lakh.
   Benefit: ₹1,000–₹10,700/year depending on class and residential status.

3. Post-Matric Scholarship for SC Students:
   Eligibility: SC students, family income < ₹2.5 lakh/year, pursuing Class 11 and above.
   Benefit: Full tuition fee reimbursement + maintenance allowance.

4. Post-Matric Scholarship for OBC Students:
   Eligibility: OBC students, family income < ₹1 lakh/year, Class 11 and above.
   Benefit: Maintenance allowance (₹1,200–₹3,000/month) + tuition fee.

5. Post-Matric Scholarship for ST Students:
   Eligibility: Scheduled Tribe students in any state, pursuing Class 11 and above.
   Benefit: Full tuition fee + boarding/lodging charges + books/stationery allowance.

6. Central Sector Scheme of Scholarship for College & University Students:
   Eligibility: Top 20 percentile of Class 12 board results, family income < ₹8 lakh/year.
   Benefit: ₹10,000–₹20,000/year at UG/PG level.

7. PM Scholarship Scheme for Central Armed Police Forces (CAPF) / Railways:
   Benefit: ₹3,000/month (boys) and ₹3,500/month (girls) for professional courses.

How to Apply: All central government scholarships — National Scholarship Portal (NSP): scholarships.gov.in.
Required Documents: Aadhaar, Bank account, Income certificate, Caste certificate (if applicable), Previous marksheet."""

FIRST_AID_DOC = """Rural Health Care Guidelines — Emergency First Aid
Source: Ministry of Health & Family Welfare, Government of India; National Health Mission (NHM)

1. Heat Stroke (Loo / Heat Exhaustion):
   • Symptoms: High body temp (>40°C), confusion, dry skin, rapid heartbeat.
   • Action: Move to cool shade immediately. Wipe body with cool damp cloth. Give ORS (Oral Rehydration Solution) if conscious. Fan the patient. Rush to nearest PHC/CHC.
   • NEVER give aspirin or paracetamol for heat stroke (worsens condition).

2. Snake Bite:
   • Keep victim calm and still — panic increases venom spread.
   • Immobilize the bitten limb at or below heart level. Splint if possible.
   • Remove rings, watch, tight clothing from bitten area.
   • Clean wound with clean water — do NOT cut, suck, or apply tourniquet.
   • Rush to hospital with antivenom facility. Note snake description if safe to do so.
   • Common antivenom: Polyvalent Anti-Snake Venom Serum (PAVS) covers Big 4 (Cobra, Krait, Russell's Viper, Saw-scaled Viper).

3. Drowning:
   • Remove from water, place on firm surface, tilt head back, give 2 rescue breaths.
   • Begin CPR immediately: 30 chest compressions (centre of chest, 2 inches deep) + 2 breaths. Continue until breathing resumes or help arrives.

4. Severe Bleeding:
   • Apply firm direct pressure with clean cloth for at least 10 minutes. Do NOT remove cloth — add more on top if blood soaks through.
   • Elevate the injured limb above heart level if no fracture suspected.
   • Tourniquet only for life-threatening limb bleed — apply 5 cm above wound, note time of application.

5. Choking (Adult):
   • If mild — encourage forceful coughing.
   • If severe — 5 back blows between shoulder blades with heel of hand; 5 abdominal thrusts (Heimlich manoeuvre). Alternate until object dislodges or patient loses consciousness.
   • Call 108 (Emergency Ambulance) immediately.

Emergency Numbers India: 108 (Ambulance), 112 (National Emergency), 1800-180-1104 (National Health Helpline)."""

CURRICULUM_DOC = """Primary Education Curriculum — National Curriculum Framework (NCF-2023)
Source: NCERT; Ministry of Education, Government of India

Foundational Stage (Age 3–8 / Pre-school to Grade 2):
• Language (Hindi / English / Regional language):
  - Identify and write all alphabets (Hindi: Devanagari 52 characters; English: 26).
  - Read simple 3–5 letter words. Form basic sentences with subject + verb.
• Numeracy:
  - Count and write numbers 1–100. Addition and subtraction with single digits.
  - Identify basic shapes (circle, square, triangle, rectangle) and patterns.
• Life Skills: Personal hygiene, road safety rules, respect for elders, environmental awareness.

Preparatory Stage (Age 8–11 / Grade 3–5):
• Mathematics: Multi-digit addition/subtraction; tables 1–20; fractions and decimals introduction; area and perimeter of simple shapes.
• Science: States of matter; plant life cycle; food and nutrition; water and air.
• Social Studies: Indian geography basics (major rivers, mountains, states); civic duties; freedom movement (key events and leaders).

Middle Stage (Age 11–14 / Grade 6–8):
• Algebra introduction; Geometry theorems (Pythagoras, angles); Statistics basics.
• Cell biology; Chemical reactions; Light and sound; Electricity basics.
• Indian constitution; Governance; Economic systems.

Mid-Day Meal (PM POSHAN) Scheme:
• Provides free cooked meals to students in government schools — Grades 1–8.
• Nutritional norms: Min 450 calories + 12g protein (primary); 700 calories + 20g protein (upper primary)."""

LEGAL_DOC = """Basic Legal Rights & Procedures — National Reference Guide
Source: Department of Justice, Ministry of Law & Justice, Government of India

1. Right to Information (RTI) Act, 2005:
   • Any citizen can file a written request to any public authority seeking information.
   • Response must be given within 30 days (48 hours for life/liberty matters).
   • Fee: ₹10 application fee. BPL card holders are exempt.
   • First Appeal: If no response or unsatisfactory response, file First Appeal with the designated First Appellate Authority within 30 days.
   • Second Appeal: File with State/Central Information Commission within 90 days.
   • Central RTI Portal: rtionline.gov.in

2. Minimum Wages Act, 1948:
   • Agricultural workers are entitled to state-notified minimum wages. Rates vary by state and crop/activity type (skilled, semi-skilled, unskilled).
   • Violations: File complaint at Office of the Labour Commissioner / District Magistrate's office.
   • Helpline: 14434 (Ministry of Labour & Employment)

3. Consumer Protection Act, 2019:
   • File complaint against defective goods or deficient services.
   • District Consumer Commission: Claims up to ₹50 lakh.
   • State Consumer Commission: Claims ₹50 lakh – ₹2 crore.
   • National Consumer Commission: Claims above ₹2 crore.
   • E-daakhil Portal: edaakhil.nic.in (file complaint online).

4. MGNREGS (Mahatma Gandhi National Rural Employment Guarantee Scheme):
   • Guarantees 100 days of wage employment per year to rural households.
   • Wages: State-notified MGNREGS wage (varies ₹210–₹357/day by state).
   • Right to Demand Work: Submit written application to local Gram Panchayat. Work must be provided within 15 days or unemployment allowance paid.
   • Application: Directly at Gram Panchayat or through the MGNREGS portal.

5. Panchayati Raj — Filing Grievances at Gram Panchayat:
   • Request for public works, road/water repair, ration card issues, welfare certificates: Submit written petition to Gram Panchayat Secretary.
   • Gram Sabha meetings (held quarterly): Any citizen can raise issues directly before elected representatives.
"""

# Seed Cloud Files (writes to knowledge_packs/ folder — simulates cloud repository)
write_cloud_file("KP-AGRI-ED-09", "wheat_cultivation_india.txt", WHEAT_INDIA_DOC)
write_cloud_file("KP-AGRI-ED-09", "rice_cultivation_india.txt", RICE_INDIA_DOC)
write_cloud_file("KP-AGRI-ED-09", "pulses_india.txt", PULSES_INDIA_DOC)
write_cloud_file("KP-AGRI-ED-09", "agricultural_subsidies.txt", AGRI_SUBSIDY_DOC)
write_cloud_file("KP-AGRI-ED-09", "soil_health.txt", SOIL_HEALTH_DOC)
write_cloud_file("KP-AGRI-ED-09", "pest_control.txt", PEST_CONTROL_DOC)

write_cloud_file("KP-SCHOLAR-2024", "scholarships.txt", SCHOLARSHIPS_DOC)
write_cloud_file("KP-HEALTH-RURAL", "first_aid.txt", FIRST_AID_DOC)
write_cloud_file("KP-EDU-PRIMARY", "curriculum.txt", CURRICULUM_DOC)
write_cloud_file("KP-LEGAL-BASIC", "legal_rights.txt", LEGAL_DOC)

# Seed Initial Device Storage — pre-installs key packs on the device
def seed_device_storage():
    import json
    
    # --- KP-SCHOLAR-2024 ---
    write_device_file("KP-SCHOLAR-2024", "scholarships.txt", SCHOLARSHIPS_DOC)
    scholarship_meta = {
        "id": "KP-SCHOLAR-2024", "title": "Government Scholarship Schemes 2024",
        "icon": "account_balance", "category": "Education", "version": "v2.1", "size_mb": 420,
        "files_count": 1,
        "files_metadata": [{"path": "scholarships.txt", "size_bytes": len(SCHOLARSHIPS_DOC), "hash": hashlib.md5(SCHOLARSHIPS_DOC.encode()).hexdigest()}]
    }
    meta_path = os.path.join(DEVICE_STORAGE_DIR, "KP-SCHOLAR-2024", "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(scholarship_meta, f, indent=2)
    index_file("KP-SCHOLAR-2024", "KP-SCHOLAR-2024/scholarships.txt", SCHOLARSHIPS_DOC)

    # --- KP-AGRI-ED-09 (National Scope) ---
    write_device_file("KP-AGRI-ED-09", "wheat_cultivation_india.txt", WHEAT_INDIA_DOC)
    write_device_file("KP-AGRI-ED-09", "rice_cultivation_india.txt", RICE_INDIA_DOC)
    write_device_file("KP-AGRI-ED-09", "pulses_india.txt", PULSES_INDIA_DOC)
    write_device_file("KP-AGRI-ED-09", "agricultural_subsidies.txt", AGRI_SUBSIDY_DOC)
    write_device_file("KP-AGRI-ED-09", "soil_health.txt", SOIL_HEALTH_DOC)
    write_device_file("KP-AGRI-ED-09", "pest_control.txt", PEST_CONTROL_DOC)

    agri_meta = {
        "id": "KP-AGRI-ED-09", "title": "Agricultural Best Practices & Crop Data",
        "icon": "agriculture", "category": "Agriculture", "version": "v2.0", "size_mb": 850,
        "files_count": 6,
        "files_metadata": [
            {"path": "wheat_cultivation_india.txt", "size_bytes": len(WHEAT_INDIA_DOC), "hash": hashlib.md5(WHEAT_INDIA_DOC.encode()).hexdigest()},
            {"path": "rice_cultivation_india.txt", "size_bytes": len(RICE_INDIA_DOC), "hash": hashlib.md5(RICE_INDIA_DOC.encode()).hexdigest()},
            {"path": "pulses_india.txt", "size_bytes": len(PULSES_INDIA_DOC), "hash": hashlib.md5(PULSES_INDIA_DOC.encode()).hexdigest()},
            {"path": "agricultural_subsidies.txt", "size_bytes": len(AGRI_SUBSIDY_DOC), "hash": hashlib.md5(AGRI_SUBSIDY_DOC.encode()).hexdigest()},
            {"path": "soil_health.txt", "size_bytes": len(SOIL_HEALTH_DOC), "hash": hashlib.md5(SOIL_HEALTH_DOC.encode()).hexdigest()},
            {"path": "pest_control.txt", "size_bytes": len(PEST_CONTROL_DOC), "hash": hashlib.md5(PEST_CONTROL_DOC.encode()).hexdigest()}
        ]
    }
    meta_path = os.path.join(DEVICE_STORAGE_DIR, "KP-AGRI-ED-09", "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(agri_meta, f, indent=2)

    index_file("KP-AGRI-ED-09", "KP-AGRI-ED-09/wheat_cultivation_india.txt", WHEAT_INDIA_DOC)
    index_file("KP-AGRI-ED-09", "KP-AGRI-ED-09/rice_cultivation_india.txt", RICE_INDIA_DOC)
    index_file("KP-AGRI-ED-09", "KP-AGRI-ED-09/pulses_india.txt", PULSES_INDIA_DOC)
    index_file("KP-AGRI-ED-09", "KP-AGRI-ED-09/agricultural_subsidies.txt", AGRI_SUBSIDY_DOC)
    index_file("KP-AGRI-ED-09", "KP-AGRI-ED-09/soil_health.txt", SOIL_HEALTH_DOC)
    index_file("KP-AGRI-ED-09", "KP-AGRI-ED-09/pest_control.txt", PEST_CONTROL_DOC)

    # --- KP-HEALTH-RURAL ---
    write_device_file("KP-HEALTH-RURAL", "first_aid.txt", FIRST_AID_DOC)
    health_meta = {
        "id": "KP-HEALTH-RURAL", "title": "Rural Healthcare First-Aid Guide",
        "icon": "local_hospital", "category": "Healthcare", "version": "v1.0", "size_mb": 1228,
        "files_count": 1,
        "files_metadata": [{"path": "first_aid.txt", "size_bytes": len(FIRST_AID_DOC), "hash": hashlib.md5(FIRST_AID_DOC.encode()).hexdigest()}]
    }
    meta_path = os.path.join(DEVICE_STORAGE_DIR, "KP-HEALTH-RURAL", "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(health_meta, f, indent=2)
    index_file("KP-HEALTH-RURAL", "KP-HEALTH-RURAL/first_aid.txt", FIRST_AID_DOC)

    # --- KP-LEGAL-BASIC ---
    write_device_file("KP-LEGAL-BASIC", "legal_rights.txt", LEGAL_DOC)
    legal_meta = {
        "id": "KP-LEGAL-BASIC", "title": "Basic Legal Rights & Procedures Manual",
        "icon": "gavel", "category": "Governance", "version": "v3.4", "size_mb": 620,
        "files_count": 1,
        "files_metadata": [{"path": "legal_rights.txt", "size_bytes": len(LEGAL_DOC), "hash": hashlib.md5(LEGAL_DOC.encode()).hexdigest()}]
    }
    meta_path = os.path.join(DEVICE_STORAGE_DIR, "KP-LEGAL-BASIC", "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(legal_meta, f, indent=2)
    index_file("KP-LEGAL-BASIC", "KP-LEGAL-BASIC/legal_rights.txt", LEGAL_DOC)


# Reseed database & vector store
seed_device_storage()

def check_offline():
    if IS_OFFLINE:
        raise HTTPException(status_code=503, detail="Simulated Offline Mode is enabled. Cannot reach server.")

# ----------------- CLOUD ENDPOINTS -----------------

@app.get("/api/packs")
def list_packs(db: Session = Depends(get_db)):
    # Always return from local SQLite cache — this is device-cached pack catalogue
    # check_offline() is intentionally NOT called: pack catalogue is always available
    packs = db.query(KnowledgePack).all()
    return packs

# Alias for explicit local pack listing
@app.get("/api/local/packs")
def list_local_packs(db: Session = Depends(get_db)):
    return list_packs(db)

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
    # Always available — this is local SQLite data, never blocked by offline mode
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

# Alias: local sync history — always works offline too
@app.get("/api/local/history")
def get_local_history(db: Session = Depends(get_db)):
    return get_sync_history(db)

@app.post("/api/sync/log")
def log_sync(req: SyncLogRequest, db: Session = Depends(get_db)):
    # Always log locally — this writes to local SQLite regardless of online/offline state
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
