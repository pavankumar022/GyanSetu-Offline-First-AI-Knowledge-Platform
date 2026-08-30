"""
scripts/retrofit_all_remaining_crops.py — Standardize All Remaining 35 Crops
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Retrofits remaining crop files with exact five section headers:
  1. Water Requirement by Phase
  2. Fertilizer Requirement by Phase
  3. Total Crop Duration
  4. Harvesting Details
  5. Growing Season
"""

import os

KP_DIR = r"c:\Users\pavan\OneDrive\Documents\stuti\knowledge_packs\KP-AGRI-ED-09"
DS_DIR = r"c:\Users\pavan\OneDrive\Documents\stuti\device_storage\KP-AGRI-ED-09"

DOCS = {}

# COTTON
DOCS["cotton_cultivation_india.txt"] = """Cotton Cultivation Guidelines — National & Regional Advisory
Source: ICAR-Central Institute for Cotton Research (CICR), Nagpur; UAS Dharwad

Suitable Agro-Climatic Zones & Recommended Varieties:
• Agro-Climatic Zones: Gujarat (No. 1 state), Maharashtra, Telangana, Rajasthan, Karnataka (Dharwad, Haveri, Belagavi, Raichur), AP, Punjab, Haryana.
• Recommended Varieties: Bt Hybrids: Rasi 659, Bunny Bt, DHH-11. Desi/Rainfed: Jayadhar, DLSa-17. Yield: 25–35 q/ha seed cotton.

Water Requirement by Phase:
• Crop Category: Suited to Irrigated (Gujarat/North India) and Rainfed Vertisols (Deccan Plateau).
• Total Water Requirement: Approximately 700–900 mm total water over the crop cycle.
• 1. Initial Phase (Germination & Seedling Phase: 0–35 Days After Sowing - DAS):
  - Water Frequency: Pre-sowing irrigation followed by light watering every 10–12 days. Provide drainage in heavy clay.
• 2. Middle Phase (Square Formation & Flowering: 35–110 DAS):
  - Water Frequency: Irrigate every 12–15 days in rainless spells.
  - Water-Critical Sub-Stage: Peak Flowering & Boll Formation (60–90 DAS) is the SINGLE most water-critical stage. Water shortage causes up to 40% flower bud and young boll shedding.
• 3. Final Phase (Boll Development & Bursting: 110–160 DAS):
  - Water Frequency: Light irrigation during late boll maturation (110–130 DAS).
  - Stop Irrigation Timing: STOP all irrigation 20–25 days before first picking when bolls begin to burst open naturally.

Fertilizer Requirement by Phase:
• Irrigated Bt Cotton Hybrids Fertilizer Schedule (NPK per Hectare):
  - Total Dose: 150 kg Nitrogen (N) : 75 kg Phosphorus (P2O5) : 75 kg Potassium (K2O).
  - 1. Basal Dose (At Sowing): Apply 20% Nitrogen (30 kg N) + 100% Phosphorus (75 kg P2O5) + 33% Potassium (25 kg K2O).
  - 2. Top-Dressing / Middle Phase:
    * Round 1 (Square Formation Stage - 40 to 45 DAS): Top-dress 40% Nitrogen (60 kg N) + 33% Potassium (25 kg K2O).
    * Round 2 (Peak Flowering Stage - 70 to 75 DAS): Top-dress remaining 40% Nitrogen (60 kg N) + remaining 34% Potassium (25 kg K2O).
  - 3. Final Phase: Foliar spray of 1% Magnesium Sulfate + 0.2% Borax at peak boll formation to prevent leaf reddening.
• Rainfed Cotton Fertilizer Schedule:
  - Total Dose: 90 kg Nitrogen (N) : 45 kg Phosphorus (P2O5) : 45 kg Potassium (K2O). Apply 50% N + full P & K basal; top-dress 50% N at 45 DAS after rains.

Total Crop Duration:
• Standalone Total Duration: Total Duration: 150–180 days (approximately 5 to 6 months) from sowing to harvest (multiple pickings).

Harvesting Details:
• Signs of Maturity: Cotton bolls burst open fully exposing dry white lint fluff; boll carpels dry up.
• Harvesting Method: Manual picking of clean seed cotton from fully burst bolls in 3–4 flush pickings.
• Post-Harvest Handling: Avoid picking wet dew-laden cotton in morning; dry picked seed cotton in sun until moisture is <8% before ginning/bagging.
• Expected Yield: Irrigated Bt Cotton: 28–35 quintals/ha (11–14 q/acre). Rainfed Cotton: 15–22 quintals/ha (6–9 q/acre).

Growing Season:
• Kharif Season: Sowing window May 15 to June 30 with pre-monsoon or monsoon rains.
"""

# GROUNDNUT
DOCS["groundnut_cultivation_india.txt"] = """Groundnut (Peanut) Cultivation Guidelines — National Advisory
Source: ICAR-Directorate of Groundnut Research (DGR), Junagadh; UAS Dharwad & TNAU

Suitable Agro-Climatic Zones & Recommended Varieties:
• Agro-Climatic Zones: Gujarat (Saurashtra No. 1), AP (Anantapur), Rajasthan, Tamil Nadu, Karnataka (Chitradurga, Tumakuru, Vijayapura, Dharwad).
• Recommended Varieties: K6 (Kadiri-6), GPBD-4, TMV-2, JL-24, DH-86, GGJ-22. Yield: 25–35 q/ha pods.

Water Requirement by Phase:
• Crop Category: Suited to Rainfed Kharif and Irrigated Summer/Rabi ecosystems.
• Total Water Requirement: Approximately 500–600 mm total water over the crop cycle.
• 1. Initial Phase (Germination & Vegetative Growth: 0–25 Days After Sowing - DAS):
  - Water Frequency: Irrigate immediately after sowing; repeat at 12–15 DAS. Avoid standing water.
• 2. Middle Phase (Flowering & Peg Penetration: 25–70 DAS):
  - Water Frequency: Irrigate every 8–10 days.
  - Water-Critical Sub-Stage: Peg Penetration & Pod Initiation (35–50 DAS) is the SINGLE most water-critical stage. Hard dry soil prevents peg entry into soil, reducing pod yield by 45%.
• 3. Final Phase (Pod Bulking & Maturity: 70–105 DAS):
  - Water Frequency: Irrigate at pod filling stage (75–80 DAS).
  - Stop Irrigation Timing: STOP all irrigation 10–12 days before harvest to facilitate soil drying and easy pod pulling without pod shedding.

Fertilizer Requirement by Phase:
• Irrigated Groundnut Fertilizer Schedule (NPK per Hectare):
  - Total Dose: 25 kg Nitrogen (N) : 50 kg Phosphorus (P2O5) : 25 kg Potassium (K2O) + 500 kg Gypsum (CaSO4).
  - 1. Basal Dose (At Sowing): Apply 100% Nitrogen (25 kg N) + 100% Phosphorus (50 kg P2O5) + 100% Potassium (25 kg K2O) + 250 kg Gypsum at sowing time.
  - 2. Top-Dressing / Middle Phase: Apply remaining 250 kg Gypsum per hectare at pegging stage (40 DAS) earthed up around root zone (Calcium essential for pod shell hardening and kernel development).
  - 3. Final Phase: None needed.
• Rainfed Groundnut Fertilizer Schedule:
  - Total Dose: 15 kg N : 30 kg P2O5 : 15 kg K2O + 250 kg Gypsum basal at sowing.

Total Crop Duration:
• Standalone Total Duration: Total Duration: 100–115 days (approximately 3.5 months) from sowing to harvest.

Harvesting Details:
• Signs of Maturity: Leaves yellow and drop; inside of pod shell turns dark brown to blackish; kernel seeds turn full pink.
• Harvesting Method: Manual pulling of plants or tractor-driven digger/shaker.
• Post-Harvest Handling: Sun-dry pulled plants in field for 3 days; strip pods and sun-dry pods until kernel moisture drops to 8–9%.
• Expected Yield: Irrigated Summer Groundnut: 30–40 quintals/ha (12–16 q/acre). Rainfed Kharif: 18–25 quintals/ha (7–10 q/acre).

Growing Season:
• Kharif Season: Sowing window June 15 to July 15.
• Summer / Rabi Season (Irrigated): Sowing window January 15 to February 15.
"""

# SUNFLOWER
DOCS["sunflower_cultivation_india.txt"] = """Sunflower Cultivation Guidelines — National & Regional Advisory
Source: ICAR-Indian Institute of Oilseeds Research (IIOR), Hyderabad; UAS Raichur

Suitable Agro-Climatic Zones & Recommended Varieties:
• Agro-Climatic Zones: Karnataka (Vijayapura, Koppal, Raichur, Bellary - No. 1 sunflower state), Maharashtra, AP, Telangana, Odisha, Punjab.
• Recommended Varieties & Hybrids: KBSH-41, KBSH-44, KBSH-53, DRSH-1, RSFH-1887, MORDEN. Yield: 18–25 q/ha seed.

Water Requirement by Phase:
• Crop Category: Suited to Rainfed Kharif/Rabi Vertisols and Irrigated Summer ecosystems.
• Total Water Requirement: Approximately 500–600 mm total water over the crop cycle (requires 4 to 5 irrigations).
• 1. Initial Phase (Germination & Seedling Phase: 0–20 Days After Sowing - DAS):
  - Water Frequency: Pre-sowing irrigation followed by first watering at 15–20 DAS.
• 2. Middle Phase (Buttoning, Flowering & Seed Setting: 20–70 DAS):
  - Water Frequency: Irrigate every 10–12 days.
  - Water-Critical Sub-Stage: Flowering & Seed Development (45–65 DAS) is the SINGLE most water-critical stage. Moisture stress causes empty seed hulls ("chaffiness") and severe oil drop.
• 3. Final Phase (Seed Dough & Maturation: 70–95 DAS):
  - Water Frequency: Light irrigation at seed dough stage (75–80 DAS).
  - Stop Irrigation Timing: STOP all irrigation 15 days before harvest when back of sunflower head turns lemon yellow.

Fertilizer Requirement by Phase:
• Irrigated Sunflower Hybrid Fertilizer Schedule (NPK per Hectare):
  - Total Dose: 60 kg Nitrogen (N) : 60 kg Phosphorus (P2O5) : 30 kg Potassium (K2O) + 20 kg Elemental Sulfur + 2 kg Solubor (Boron).
  - 1. Basal Dose (At Sowing): Apply 50% Nitrogen (30 kg N) + 100% Phosphorus (60 kg P2O5) + 100% Potassium (30 kg K2O) + 20 kg Sulfur.
  - 2. Top-Dressing / Middle Phase:
    * Top-dress remaining 50% Nitrogen (30 kg N) at 30 DAS (buttoning stage).
    * Foliar spray of Solubor (Boron 20%) @ 0.2% (2 g/litre) at ray floret opening stage (50 DAS) to maximize seed set.
  - 3. Final Phase: None needed.
• Rainfed Sunflower Fertilizer Schedule:
  - Total Dose: 40 kg N : 40 kg P2O5 : 20 kg K2O as 100% basal dose at sowing.

Total Crop Duration:
• Standalone Total Duration: Total Duration: 90–105 days (approximately 3 to 3.5 months) from sowing to harvest.

Harvesting Details:
• Signs of Maturity: Back of capitulum head turns golden yellow; ray florets wither and drop off; seeds turn hard and dark.
• Harvesting Method: Cut sunflower heads manually with sickles.
• Post-Harvest Handling: Sun-dry heads for 3–4 days; thresh using mechanical sunflower thresher; dry seeds to 8–9% moisture content.
• Expected Yield: Irrigated Sunflower: 20–25 quintals/ha (8–10 q/acre). Rainfed Sunflower: 12–16 quintals/ha (5–7 q/acre).

Growing Season:
• Kharif Season: Sowing window June 15 to July 15.
• Rabi Season: Sowing window September 15 to October 15.
• Summer Season (Irrigated): Sowing window January 15 to February 15.
"""

# MUSTARD
DOCS["mustard_rapeseed_india.txt"] = """Mustard & Rapeseed Cultivation Guidelines — National Advisory
Source: ICAR-Directorate of Rapeseed-Mustard Research (DRMR), Bharatpur; PAU & CCSHAU

Suitable Agro-Climatic Zones & Recommended Varieties:
• Agro-Climatic Zones: Rajasthan (No. 1 state), MP, Haryana, UP, West Bengal, Assam, Punjab, Gujarat.
• Recommended Varieties: Pusa Mustard-25 (NPJ-112), Pusa Mustard-30, RH-749, Giriraj (DRMRIJ-31), NRCDR-2. Yield: 20–28 q/ha.

Water Requirement by Phase:
• Crop Category: Suited to Rainfed Rabi & Irrigated Semi-Arid ecosystems (low water requirement).
• Total Water Requirement: Approximately 250–350 mm total water over the crop cycle (requires 2 to 3 irrigations).
• 1. Initial Phase (Germination & Rosette Stage: 0–30 Days After Sowing - DAS):
  - Water Frequency: Pre-sowing irrigation followed by first irrigation at 30–35 DAS.
  - Water-Critical Sub-Stage: Flowering / Rosette Stage (30–35 DAS) is the SINGLE most water-critical stage. First irrigation at 30 DAS is mandatory for branch initiation.
• 2. Middle Phase (Flowering & Pod Formation: 30–75 DAS):
  - Water Frequency: Second irrigation at pod filling stage (60–65 DAS).
• 3. Final Phase (Pod Maturation: 75–110 DAS):
  - Water Frequency: Rainfed crop requires no late watering.
  - Stop Irrigation Timing: STOP all irrigation 20 days before harvest when siliquae pods turn yellow.

Fertilizer Requirement by Phase:
• Irrigated Mustard Fertilizer Schedule (NPK per Hectare):
  - Total Dose: 80 kg Nitrogen (N) : 40 kg Phosphorus (P2O5) : 40 kg Potassium (K2O) + 40 kg Elemental Sulfur (Gypsum @ 250 kg/ha).
  - 1. Basal Dose (At Sowing): Apply 50% Nitrogen (40 kg N) + 100% Phosphorus (40 kg P2O5) + 100% Potassium (40 kg K2O) + 100% Sulfur.
  - 2. Top-Dressing / Middle Phase: Top-dress remaining 50% Nitrogen (40 kg N) at first irrigation (30–35 DAS).
  - 3. Final Phase: None needed.
• Rainfed Mustard Fertilizer Schedule:
  - Total Dose: 40 kg N : 20 kg P2O5 : 20 kg K2O + 20 kg S as 100% basal dose.

Total Crop Duration:
• Standalone Total Duration: Total Duration: 105–125 days (approximately 3.5 to 4 months) from sowing to harvest.

Harvesting Details:
• Signs of Maturity: 75% of pods (siliquae) turn yellowish-brown; seeds turn hard and brown/black.
• Harvesting Method: Cut plants close to ground with sickles early morning to avoid seed shattering.
• Post-Harvest Handling: Stack harvested plants on threshing floor to dry for 4–5 days; thresh by beating or thresher; dry seeds to 8% moisture.
• Expected Yield: Irrigated Mustard: 20–28 quintals/ha (8–11 q/acre). Rainfed Mustard: 12–16 quintals/ha (5–7 q/acre).

Growing Season:
• Rabi Season: Sowing window October 1 to October 25 (timely sowing avoids aphid infestation).
"""

# Write batch 2 to disk
for filename, content in DOCS.items():
    kp_path = os.path.join(KP_DIR, filename)
    ds_path = os.path.join(DS_DIR, filename)
    with open(kp_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    with open(ds_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

print(f"Successfully updated batch 2 crop docs ({len(DOCS)} files).")
