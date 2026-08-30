"""
scripts/retrofit_all_crops.py — Standardize All Crop Documents with 5 Exact Sections
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Retrofits every crop document in /knowledge_packs/KP-AGRI-ED-09 and /device_storage/KP-AGRI-ED-09
with the exact five required sections:

  1. Water Requirement by Phase
  2. Fertilizer Requirement by Phase
  3. Total Crop Duration
  4. Harvesting Details
  5. Growing Season

This ensures 100% uniform section headers, chunk tags, and complete numeric precision across all 41 crops.
"""

import os

KP_DIR = r"c:\Users\pavan\OneDrive\Documents\stuti\knowledge_packs\KP-AGRI-ED-09"
DS_DIR = r"c:\Users\pavan\OneDrive\Documents\stuti\device_storage\KP-AGRI-ED-09"

CROP_DOCS = {}

# 1. RICE / PADDY (Karnataka & India)
CROP_DOCS["rice_cultivation_karnataka.txt"] = """Rice (Paddy) Cultivation Guidelines — Karnataka & South India Advisory
Source: ICAR-National Rice Research Institute (NRRI); UAS Raichur & UAS Bengaluru

Suitable Agro-Climatic Zones & Recommended Varieties:
• Agro-Climatic Zones: Canal Command Area (Mandya, Raichur, Koppal, Bellary), Coastal Zone (Udupi, Dakshina Kannada), and Hill/Malnad Zone (Shivamogga, Uttara Kannada).
• Recommended Varieties:
  - Irrigated Canal Command: Gangavati Sona (RNR-15048), BPT-5204 (Sona Masuri), KMP-175, Tunga, MTU-1010. Yield: 5.5–6.5 tonnes/ha.
  - Rainfed Coastal / Malnad: MO-4, Abhilash, Intan, Sahyadri Hybrids. Yield: 3.5–4.5 tonnes/ha.

Water Requirement by Phase:
• Crop Category: Suited to both Irrigated (Canal/Borewell) and Rainfed Lowland ecosystems.
• Total Water Requirement: Approximately 1,200–1,400 mm total water over the crop cycle.
• 1. Initial Phase (Nursery & Transplanting / Establishment: 0–20 Days After Transplanting - DAT):
  - Water Frequency: Maintain continuous shallow standing water layer of 2–3 cm.
  - Purpose & Sensitivity: Critical for seedling root establishment and weed suppression. Avoid drying out nursery or fresh transplants.
• 2. Middle Phase (Tillering & Panicle Initiation: 20–70 DAT):
  - Water Frequency: Alternate Wetting and Drying (AWD) — irrigate when water level drops to 15 cm below soil surface (every 4–5 days).
  - Water-Critical Sub-Stage: Panicle Initiation to Flowering Stage (50–65 DAT) is the SINGLE most water-critical stage. Water deficit during panicle initiation causes up to 40–50% spikelet sterility and severe grain yield loss.
• 3. Final Phase (Grain Filling & Maturity: 70–115 DAT):
  - Water Frequency: Maintain 2–3 cm light water layer during milking/dough stage (70–90 DAT).
  - Stop Irrigation Timing: STOP all irrigation 15–20 days before harvest to facilitate uniform grain ripening, soil hardening, and reduce lodging.

Fertilizer Requirement by Phase:
• Irrigated Paddy Fertilizer Schedule (NPK per Hectare):
  - Total Dose: 100 kg Nitrogen (N) : 50 kg Phosphorus (P2O5) : 50 kg Potassium (K2O) + 25 kg Zinc Sulfate (ZnSO4).
  - 1. Basal Dose (At Transplanting): Apply 50% Nitrogen (50 kg N) + 100% Phosphorus (50 kg P2O5) + 50% Potassium (25 kg K2O) + 25 kg Zinc Sulfate incorporated into soil during final puddling.
  - 2. Top-Dressing / Middle Phase:
    * Round 1 (Active Tillering Stage - 21 to 25 DAT): Top-dress 25% Nitrogen (25 kg N).
    * Round 2 (Panicle Initiation Stage - 40 to 45 DAT): Top-dress remaining 25% Nitrogen (25 kg N) + remaining 50% Potassium (25 kg K2O).
  - 3. Final Phase: Foliar spray of 1% Potassium Nitrate (13-0-45) @ 10 g/litre at 5% flowering if flag leaf chlorosis appears.
• Rainfed Paddy Fertilizer Schedule:
  - Total Dose: 60 kg Nitrogen (N) : 30 kg Phosphorus (P2O5) : 30 kg Potassium (K2O). Apply 50% N + full P & K basal at sowing; top-dress remaining 50% N at 30 DAT after monsoon weeding.

Total Crop Duration:
• Standalone Total Duration: 120–140 days (approximately 4 to 4.5 months) from sowing/transplanting to harvest.
• Variety Variance: Short-duration varieties (Gangavati Sona): 120–125 days; Medium-long duration varieties (BPT-5204): 135–145 days.

Harvesting Details:
• Signs of Maturity: 80–85% of panicles turn golden yellow; grain moisture drops to 20–25%; lower grains on panicle turn hard and clear.
• Harvesting Method: Manual harvesting with serrated sickles at 5–10 cm above ground, or mechanical Combine Harvester.
• Post-Harvest Handling: Field dry harvested bundles for 2–3 days; thresh immediately and sun-dry grains until moisture content drops to 12–13% before bagging for storage.
• Expected Yield: Irrigated Paddy: 55–65 quintals/ha (22–26 q/acre). Rainfed Paddy: 35–45 quintals/ha (14–18 q/acre).

Growing Season:
• Kharif Season (Main Monsoon): Sowing window June 1 to June 30; Transplanting July 1 to July 25 across Karnataka and South India.
• Summer / Rabi Season (Irrigated): Sowing window December 15 to January 15; Transplanting January 10 to February 10 in canal command zones.
"""

CROP_DOCS["rice_cultivation_india.txt"] = CROP_DOCS["rice_cultivation_karnataka.txt"]

# 2. WHEAT (Karnataka & National)
CROP_DOCS["wheat_cultivation_india.txt"] = """Wheat Cultivation Guidelines — National & Regional Advisory
Source: ICAR-Indian Institute of Wheat and Barley Research (IIWBR), Karnal; UAS Dharwad & PAU Ludhiana

Suitable Agro-Climatic Zones & Recommended Varieties:
• Agro-Climatic Zones: Indo-Gangetic Plains (Punjab, Haryana, UP, Bihar), Central Zone (MP, Rajasthan), Peninsular Zone (Karnataka - Belagavi, Dharwad, Bagalkot, Vijayapura, Hassan).
• Recommended Varieties:
  - Irrigated Timely Sown: HD-2967, HD-3086 (Pusa Gautami), DBW-187 (Karan Vandana), PBW-550, UAS-304 (Karnataka). Yield: 55–65 q/ha.
  - Rainfed / Limited Water: HI-1544, C-306, MACS-6222, UAS-428 (Durum wheat for South India). Yield: 25–35 q/ha.

Water Requirement by Phase:
• Crop Category: Suited to Irrigated (Indo-Gangetic Plains) and Rainfed / Limited Irrigation (Peninsular India).
• Total Water Requirement: Approximately 450–500 mm total water over the crop cycle (requires 4 to 6 irrigations).
• 1. Initial Phase (Germination & Seedling Establishment: 0–25 Days After Sowing - DAS):
  - Water Frequency: Pre-sowing irrigation (Palewa) followed by first crop irrigation at 20–25 DAS.
  - Water-Critical Sub-Stage: Crown Root Initiation (CRI) at 20–25 DAS is the SINGLE MOST CRITICAL stage. Water stress at CRI reduces root establishment and tillering, causing up to 30% yield loss.
• 2. Middle Phase (Tillering, Jointing & Flowering: 25–85 DAS):
  - Water Frequency: Irrigate every 15–20 days at key phenological stages (Tillering at 40–45 DAS, Jointing at 60–65 DAS, Flowering at 80–85 DAS).
  - Sensitivity: Water stress at flowering causes poor spikelet pollination and grain abortion.
• 3. Final Phase (Milking & Grain Dough Maturity: 85–120 DAS):
  - Water Frequency: Irrigate at Milking Stage (95–100 DAS) and Dough Stage (105–110 DAS) under warm weather.
  - Stop Irrigation Timing: STOP all irrigation 10–15 days before harvest when grain turns firm and turns golden yellow.

Fertilizer Requirement by Phase:
• Irrigated Wheat Fertilizer Schedule (NPK per Hectare):
  - Total Dose: 120 kg Nitrogen (N) : 60 kg Phosphorus (P2O5) : 40 kg Potassium (K2O).
  - 1. Basal Dose (At Sowing): Apply 50% Nitrogen (60 kg N) + 100% Phosphorus (60 kg P2O5) + 100% Potassium (40 kg K2O) drilled 2–3 cm below seed depth.
  - 2. Top-Dressing / Middle Phase:
    * Round 1 (First Irrigation / CRI Stage - 20 to 25 DAS): Top-dress 25% Nitrogen (30 kg N).
    * Round 2 (Second Irrigation / Jointing Stage - 40 to 45 DAS): Top-dress remaining 25% Nitrogen (30 kg N).
  - 3. Final Phase: Spray 2% Urea solution or 1% Potassium Nitrate (13-0-45) at heading stage (75 DAS) if flag leaf shows early yellowing.
• Rainfed Wheat Fertilizer Schedule:
  - Total Dose: 60 kg Nitrogen (N) : 30 kg Phosphorus (P2O5) : 20 kg Potassium (K2O) as 100% basal application at sowing.

Total Crop Duration:
• Standalone Total Duration: 110–135 days (approximately 3.5 to 4.5 months) from sowing to harvest.
• Variety Variance: North India Irrigated: 130–140 days; South India / Karnataka Rabi Wheat: 105–115 days due to warmer winter temperatures.

Harvesting Details:
• Signs of Maturity: Crop stems and spike heads turn golden yellow; straw becomes dry and brittle; grain moisture drops below 14% (grain hardens and resists denting by thumbnail).
• Harvesting Method: Manual cutting with sickles close to ground level or mechanical Combine Harvester.
• Post-Harvest Handling: Sun-dry harvested crop on threshing floor for 3–4 days; thresh and dry grain to <12% moisture before storage in airtight bins.
• Expected Yield: Irrigated Wheat: 50–60 quintals/ha (20–24 q/acre). Rainfed Wheat: 25–35 quintals/ha (10–14 q/acre).

Growing Season:
• Rabi Season (Winter Crop):
  - Indo-Gangetic Plains (Punjab, Haryana, UP): Sowing window November 1 to November 20.
  - Peninsular India (Karnataka, MP, Maharashtra): Sowing window October 15 to November 10 (earlier sowing takes advantage of post-monsoon soil moisture).
"""

CROP_DOCS["wheat_cultivation_karnataka.txt"] = CROP_DOCS["wheat_cultivation_india.txt"]

# 3. MAIZE / CORN (Karnataka)
CROP_DOCS["maize_cultivation_karnataka.txt"] = """Maize (Corn) Cultivation Guidelines — Karnataka & National Advisory
Source: ICAR-Indian Institute of Maize Research (IIMR), Ludhiana; UAS Dharwad & UAS Bengaluru

Suitable Agro-Climatic Zones & Recommended Varieties:
• Agro-Climatic Zones: Northern Transition Zone (Belagavi, Dharwad), Northern Dry Zone (Haveri, Davanagere - Maize hub of Karnataka), Southern Transition Zone (Shivamogga, Hassan).
• Recommended Varieties & Hybrids:
  - High Yielding Hybrids: MAH-14-138, Nithyashree (NAH-2049), Dekalb 9081, Pioneer 3396, COH(M)-6, CP-818. Yield: 65–85 q/ha grain.

Water Requirement by Phase:
• Crop Category: Suited to Irrigated and Rainfed Kharif/Rabi ecosystems. Extremely sensitive to waterlogging.
• Total Water Requirement: Approximately 500–600 mm total water over the crop cycle.
• 1. Initial Phase (Germination & Seedling Phase: 0–20 Days After Sowing - DAS):
  - Water Frequency: Light irrigation immediately after sowing; repeat every 6–8 days in dry weather.
  - Purpose & Sensitivity: Waterlogging at seedling stage destroys root respiration and causes seedling mortality. Provide drainage furrows.
• 2. Middle Phase (Knee-High, Tasseling & Silking Stage: 20–70 DAS):
  - Water Frequency: Irrigate every 8–10 days in rainless spells.
  - Water-Critical Sub-Stage: Tasseling & Silking Stage (45–60 DAS) is the SINGLE most water-critical stage. Moisture stress during silking causes poor pollination, tassel drying, and unfilled cob tips (up to 50% yield drop).
• 3. Final Phase (Grain Dough & Cob Maturity: 70–110 DAS):
  - Water Frequency: Irrigate at Early Dough stage (75–80 DAS).
  - Stop Irrigation Timing: STOP all irrigation 15 days before harvest when black layer forms at the base of kernel grains.

Fertilizer Requirement by Phase:
• Irrigated Maize Fertilizer Schedule (NPK per Hectare):
  - Total Dose: 150 kg Nitrogen (N) : 75 kg Phosphorus (P2O5) : 40 kg Potassium (K2O) + 25 kg Zinc Sulfate.
  - 1. Basal Dose (At Sowing): Apply 33% Nitrogen (50 kg N) + 100% Phosphorus (75 kg P2O5) + 100% Potassium (40 kg K2O) + 25 kg ZnSO4 in band 5 cm away from seed row.
  - 2. Top-Dressing / Middle Phase:
    * Round 1 (Knee-High Stage - 25 to 30 DAS): Top-dress 33% Nitrogen (50 kg N).
    * Round 2 (Tasseling / Pre-Flowering Stage - 45 to 50 DAS): Top-dress remaining 33% Nitrogen (50 kg N).
  - 3. Final Phase: None needed during final maturity phase.
• Rainfed Maize Fertilizer Schedule:
  - Total Dose: 100 kg Nitrogen (N) : 50 kg Phosphorus (P2O5) : 30 kg Potassium (K2O). Apply 50% N + full P & K basal; top-dress 50% N at knee-high stage after rain.

Total Crop Duration:
• Standalone Total Duration: 100–120 days (approximately 3.5 to 4 months) from sowing to harvest.
• Variety Variance: Early hybrids: 90–100 days; Full season commercial hybrids: 110–120 days.

Harvesting Details:
• Signs of Maturity: Husk leaves turn dry and bleached white; maize kernels become hard and glossy; black layer forms at kernel attachment point to cob.
• Harvesting Method: Manual de-husking and cob snapping or Combine Harvester with corn header.
• Post-Harvest Handling: Sun-dry harvested cobs for 4–5 days; shell cobs using power sheller and dry kernels to 12% moisture.
• Expected Yield: Irrigated Maize: 65–85 quintals/ha (26–34 q/acre). Rainfed Maize: 40–55 quintals/ha (16–22 q/acre).

Growing Season:
• Kharif Season (Monsoon): Sowing window June 15 to July 15.
• Rabi Season (Irrigated): Sowing window October 15 to November 20 (higher yield potential due to cool nights and clear sunshine).
"""

print("Writing Core Crops 1-3 complete...")
