"""
scripts/retrofit_batch3.py — Standardize All Remaining Horticulture, Pulses, Oilseeds & Plantation Crops
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

# SOYBEAN
DOCS["soybean_cultivation_india.txt"] = """Soybean Cultivation Guidelines — National Advisory
Source: ICAR-Indian Institute of Soybean Research (IISR), Indore; MPKV Rahuri & UAS Dharwad

Suitable Agro-Climatic Zones & Recommended Varieties:
• Agro-Climatic Zones: MP (Malwa plateau No. 1 state), Maharashtra (Latur, Amravati), Rajasthan (Kota), Karnataka (Belagavi, Bidar).
• Recommended Varieties: JS-335, JS-9560, JS-2034, DSb-21 (Karnataka), MACS-1407. Yield: 22–30 q/ha.

Water Requirement by Phase:
• Crop Category: Suited to Rainfed Kharif ecosystems; sensitive to waterlogging.
• Total Water Requirement: Approximately 450–500 mm total water over the crop cycle.
• 1. Initial Phase (Germination & Seedling Establishment: 0–20 Days After Sowing - DAS):
  - Water Frequency: Rainfed monsoon crop. Ensure field drainage.
• 2. Middle Phase (Branching, Flowering & Pod Initiation: 20–70 DAS):
  - Water Frequency: Irrigate at 35 DAS and 55 DAS if rain fails.
  - Water-Critical Sub-Stage: Flowering & Pod Filling Stage (40–65 DAS) is the SINGLE most water-critical stage. Moisture stress causes up to 40% pod drop.
• 3. Final Phase (Pod Maturation: 70–95 DAS):
  - Water Frequency: Rainfed crop requires no late watering.
  - Stop Irrigation Timing: STOP all irrigation 15 days before harvest when leaves turn yellow and drop off.

Fertilizer Requirement by Phase:
• Rainfed Soybean Fertilizer Schedule (NPK per Hectare):
  - Total Dose: 30 kg Nitrogen (N) : 60 kg Phosphorus (P2O5) : 30 kg Potassium (K2O) + 20 kg Elemental Sulfur.
  - 1. Basal Dose (At Sowing): Apply 100% N, P, K, and S at sowing + Bradyrhizobium japonicum inoculation.
  - 2. Top-Dressing / Middle Phase: Foliar spray of 2% DAP or 1% 19-19-19 at flowering (45 DAS).
  - 3. Final Phase: None needed.

Total Crop Duration:
• Standalone Total Duration: Total Duration: 90–105 days (approximately 3 to 3.5 months) from sowing to harvest.

Harvesting Details:
• Signs of Maturity: 95% of leaves turn yellow and drop off; pods turn golden brown; seeds rattle inside pods.
• Harvesting Method: Cut plants close to ground with sickles or use soybean Combine Harvester.
• Post-Harvest Handling: Field dry bundles for 2–3 days; thresh and dry seed to <10% moisture content.
• Expected Yield: Rainfed Soybean: 22–30 quintals/ha (9–12 q/acre).

Growing Season:
• Kharif Season: Sowing window June 15 to July 10 (with arrival of monsoon rains).
"""

# MOONG, URAD & LENTIL
DOCS["moong_urad_lentil_pulses.txt"] = """Green Gram (Moong), Black Gram (Urad) & Lentil (Masoor) Guidelines — National Advisory
Source: ICAR-IIPR Kanpur; UAS Dharwad & TNAU

Suitable Agro-Climatic Zones & Recommended Varieties:
• Moong (Green Gram): IPM 02-3, HUM-16, DGG-5 (Karnataka). Urad: LBG-752, DU-1. Lentil: L-4076, HUL-57. Yield: 10–18 q/ha.

Water Requirement by Phase:
• Crop Category: Rainfed Kharif / Rice Fallows; Irrigated Summer (Zaid).
• Total Water Requirement: Approximately 300–400 mm.
• 1. Initial Phase (Germination & Seedling: 0–15 DAS): Light watering for summer crop; rainfed for Kharif.
• 2. Middle Phase (Branching & Flowering: 15–50 DAS): Irrigate summer crop every 8–10 days. Flowering & Pod Development (30–45 DAS) is the SINGLE most water-critical stage.
• 3. Final Phase (Pod Maturation: 50–70 DAS): STOP all irrigation 10 days before harvest when pods turn black/brown.

Fertilizer Requirement by Phase:
• Pulse Fertilizer Schedule (NPK per Hectare):
  - Total Dose: 20 kg Nitrogen (N) : 40 kg Phosphorus (P2O5) : 20 kg Potassium (K2O) + 20 kg Sulfur.
  - 1. Basal Dose: 100% N, P, K, and S at sowing + Rhizobium seed inoculation.
  - 2. Top-Dressing / Middle Phase: Foliar spray of 2% DAP at 35 DAS.
  - 3. Final Phase: None.

Total Crop Duration:
• Standalone Total Duration: Total Duration: 65–75 days (approximately 2 to 2.5 months) for Moong/Urad; 110–120 days for Lentil.

Harvesting Details:
• Signs of Maturity: 85% of pods turn dark brown or black; leaves yellow and dry.
• Harvesting Method: Hand picking mature pods in flushes or cut whole plants.
• Post-Harvest Handling: Sun-dry pods for 3 days; thresh and dry seeds to 9% moisture.
• Expected Yield: Kharif Pulses: 10–12 q/ha. Summer Irrigated Pulses: 14–18 q/ha.

Growing Season:
• Kharif: June 15 to July 15. Summer (Zaid): March 1 to March 25. Rabi Rice Fallows: October 15 to November 15.
"""

# SESAME & CASTOR
DOCS["sesame_castor_oilseeds.txt"] = """Sesame (Til) & Castor Cultivation Guidelines — National Advisory
Source: ICAR-DOR Hyderabad; JAU Junagadh & UAS Raichur

Suitable Agro-Climatic Zones & Recommended Varieties:
• Sesame: RT-351, DS-5 (Karnataka). Castor: GCH-7, DCH-519, DCH-177. Yield: Sesame 8–12 q/ha; Castor 20–30 q/ha.

Water Requirement by Phase:
• Crop Category: Rainfed Kharif; Drip / Furrow Irrigated Summer Sesame & Castor.
• Total Water Requirement: Sesame 300 mm; Castor 500–600 mm.
• 1. Initial Phase (Germination: 0–15 DAS): Light watering for summer crop; rainfed for Kharif.
• 2. Middle Phase (Flowering & Capsule / Spike Bulking: 15–75 DAS): Main Spike Flowering (45 DAS) is the SINGLE most water-critical stage.
• 3. Final Phase (Maturity: 75–120 DAS): STOP irrigation 15 days before harvest when leaves turn yellow.

Fertilizer Requirement by Phase:
• Sesame Dose: 40 kg N : 20 kg P2O5 : 20 kg K2O + 20 kg S (100% basal).
• Castor Dose: 80 kg N : 40 kg P2O5 : 30 kg K2O (50% N basal, 25% at 30 DAS, 25% at 60 DAS).

Total Crop Duration:
• Standalone Total Duration: Total Duration: 80–90 days for Sesame; 150–180 days (5 to 6 months) for Castor (multiple pickings).

Harvesting Details:
• Signs of Maturity: Sesame leaves yellow; lower capsules turn yellow. Castor spikes turn light brown and dry.
• Harvesting Method: Cut sesame plants and dry vertically; hand pick castor spikes in 3–4 pickings.
• Expected Yield: Sesame: 8–12 q/ha. Castor: 20–30 q/ha.

Growing Season:
• Kharif: June 15 to July 15. Summer Sesame: Jan 15 to Feb 15. Rabi Castor: August 15 to Sept 15.
"""

# JUTE & TOBACCO
DOCS["jute_tobacco_cash_crops.txt"] = """Jute & Tobacco Cash Crops Guidelines — National Advisory
Source: ICAR-CRIJAF Barrackpore; ICAR-CTRI Rajahmundry

Suitable Agro-Climatic Zones & Recommended Varieties:
• Jute: JRO-204, JRC-698 (WB, Assam, Bihar). Tobacco: Kanchan, Siri (AP, Mysuru KA). Yield: Jute 30–40 q/ha fibre; Tobacco 20–25 q/ha leaf.

Water Requirement by Phase:
• Crop Category: Jute: Pre-monsoon irrigated/Rainfed; Tobacco: Light furrow irrigated.
• 1. Initial Phase (Nursery & Transplanting: 0–30 Days): Light watering.
• 2. Middle Phase (Vegetative Growth & Topping: 30–90 Days): Grand Vegetative Growth (45–60 Days) is the SINGLE most water-critical stage.
• 3. Final Phase (Maturity & Harvest: 90–120 Days): STOP watering 15 days before harvest.

Fertilizer Requirement by Phase:
• Jute: 80 kg N : 40 kg P2O5 : 40 kg K2O.
• Tobacco: 40 kg N : 60 kg P2O5 : 120 kg K2O (High Potash non-chloride form).

Total Crop Duration:
• Standalone Total Duration: Total Duration: 120 days (4 months) for Jute; 120–140 days for Tobacco.

Harvesting Details:
• Signs of Maturity: Jute harvested at 50% flowering (small pod stage). Tobacco leaves turn yellowish-green with gummy feel.
• Expected Yield: Jute: 30–40 q/ha fibre. Tobacco: 20–25 q/ha leaf.

Growing Season:
• Jute: March 15 to April 30. Tobacco: Transplanting Sept 15 to Oct 15 (Rabi).
"""

# BANANA
DOCS["banana_cultivation_india.txt"] = """Banana Cultivation Guidelines — National & Regional Advisory
Source: ICAR-National Research Centre for Banana (NRCB), Tiruchirappalli; IIHR Bengaluru

Suitable Agro-Climatic Zones & Recommended Varieties:
• Agro-Climatic Zones: AP, Maharashtra (Jalgaon hub), Tamil Nadu, Karnataka (Mysuru, Nanjangud, Hassan).
• Recommended Varieties: Grand Naine (G9 - Tissue culture), Robusta, Dwarf Cavendish, Elakki (Yelakki Rasabale). Yield: 60–80 tonnes/ha.

Water Requirement by Phase:
• Crop Category: Suited to High-Water Drip / Basin Irrigated orchards.
• Total Water Requirement: Approximately 1,800–2,000 mm total water over the 11–12 month crop cycle.
• 1. Initial Phase (Establishment: 0–3 Months After Planting - MAP): Drip 10–15 litres/plant/day every 2 days.
• 2. Middle Phase (Grand Vegetative Growth & Bunch Emergence: 4–8 MAP): Drip 20–25 litres/plant/day. Flowering / Bunch Emergence Stage (6–7 MAP) is the SINGLE most water-critical stage.
• 3. Final Phase (Bunch Development & Maturity: 9–11 MAP): Drip 15–20 L/day. STOP irrigation 10 days before harvesting bunch.

Fertilizer Requirement by Phase:
• Irrigated Banana Fertilizer Schedule (NPK per Plant / Year):
  - Total Dose: 200 g Nitrogen (N) : 50 g Phosphorus (P2O5) : 300 g Potassium (K2O) + 10 kg FYM per plant.
  - Split in 6 equal bi-monthly fertigation doses from 2nd month to 8th month.

Total Crop Duration:
• Standalone Total Duration: Total Duration: 330–365 days (approximately 11 to 12 months) from planting to harvest.

Harvesting Details:
• Signs of Maturity: Fruit angles become rounded; top leaves yellow; fingers turn bright green and plump.
• Expected Yield: Grand Naine: 60–80 tonnes/ha (25–32 t/acre). Yelakki: 35–45 tonnes/ha.

Growing Season:
• Planting Window: June to August (monsoon onset) or October–November.
"""

# MANGO, PAPAYA, GRAPES, POMEGRANATE, CITRUS
DOCS["mango_papaya_grapes_pomegranate_citrus.txt"] = """Horticulture Fruit Crops Guidelines — Mango, Papaya, Grapes, Pomegranate & Citrus
Source: ICAR-IIHR Bengaluru; ICAR-CISH Lucknow & ICAR-NRCP Solapur

Suitable Agro-Climatic Zones & Recommended Varieties:
• Mango: Alphonso, Banganapalli, Kesar, Amrapali. Papaya: Red Lady 786. Grapes: Thompson Seedless. Pomegranate: Bhagwa. Citrus: Kagzi Lime, Nagpur Mandarin.

Water Requirement by Phase:
• Drip Irrigated Orchards.
• Critical Stages: Papaya (Flowering 4 MAP), Grapes (Fruit Set Oct–Nov), Pomegranate (Bahar Flowering), Mango (Fruit Set Feb–March).
• STOP Irrigation: Grapes 15 days before harvest (°Brix > 18); Mango 20 days before harvest.

Fertilizer Requirement by Phase:
• Mango Bearing Tree: 1,000 g N : 500 g P2O5 : 1,000 g K2O/tree/year.
• Papaya: 250 g N : 250 g P2O5 : 500 g K2O/plant/year in 6 split doses.
• Pomegranate: 625 g N : 250 g P2O5 : 500 g K2O/tree/year.

Total Crop Duration:
• Standalone Total Duration: Total Duration: Papaya 9–10 months; Grapes 135–150 days post pruning; Pomegranate 150–180 days post Bahar; Mango 110–120 days from fruit set.

Harvesting Details:
• Signs of Maturity: Grapes °Brix > 18; Pomegranate dark red rind; Papaya yellow tinge at apex.
• Expected Yield: Mango: 10–15 t/ha; Papaya: 80–100 t/ha; Grapes: 25–30 t/ha; Pomegranate: 15–20 t/ha.

Growing Season:
• Planting: June–August. Fruit Harvest: Mango (April–June), Grapes (March–April), Pomegranate (Year-round Bahar).
"""

# TOMATO
DOCS["tomato_cultivation_india.txt"] = """Tomato Cultivation Guidelines — National & Karnataka Advisory
Source: ICAR-IIHR Bengaluru; IARI New Delhi

Suitable Agro-Climatic Zones & Recommended Varieties:
• Agro-Climatic Zones: Karnataka (Kolar No. 1, Chikkaballapur), AP, MP, Maharashtra, WB.
• Recommended Varieties: Arka Rakshak, Arka Samrat, Pusa Ruby, PKM-1, Heemsena. Yield: 50–75 tonnes/ha.

Water Requirement by Phase:
• Category: Irrigated Drip / Staking. Total Water: 400–600 mm.
• 1. Initial (0–20 DAT): Drip irrigate every 2–3 days.
• 2. Middle (20–60 DAT): Flowering & Fruit Development (30–50 DAT) is the SINGLE most water-critical stage. Water stress causes blossom end rot and fruit cracking.
• 3. Final (60–100 DAT): Irrigate every 4–5 days during picking. Stop 7 days before final clearing.

Fertilizer Requirement by Phase:
• Total Dose: 180 kg N : 120 kg P2O5 : 150 kg K2O. Basal: 50% N + 100% P + 50% K. Top-dress remaining 50% N and K in 3 split fertigation rounds at 20, 40, 60 DAT.

Total Crop Duration:
• Standalone Total Duration: Total Duration: 110–130 days (approximately 3.5 to 4 months) from transplanting to final harvest.

Harvesting Details:
• Maturity: Breaker stage (pinkish red at blossom end) for distant transport; full red for local market.
• Expected Yield: 50–75 tonnes/ha (20–30 t/acre).

Growing Season:
• Kharif: June–July; Rabi: Oct–Nov; Summer: Jan–Feb.
"""

# ONION
DOCS["onion_cultivation_india.txt"] = """Onion Cultivation Guidelines — National Advisory
Source: ICAR-Directorate of Onion and Garlic Research (DOGR), Rajgurunagar; DOGR Pune

Suitable Agro-Climatic Zones & Recommended Varieties:
• Agro-Climatic Zones: Maharashtra (Nashik No. 1), Karnataka (Vijayapura, Gadag, Bagalkot), Gujarat, MP.
• Recommended Varieties: Bhima Super, Bhima Dark Red, N-2-4-1, Arka Kalyan. Yield: 25–35 tonnes/ha.

Water Requirement by Phase:
• Category: Irrigated Drip / Surface. Total Water: 400–500 mm.
• 1. Initial (0–30 DAT): Irrigate every 5–7 days.
• 2. Middle (30–75 DAT): Bulb Development Stage (45–65 DAT) is the SINGLE most water-critical stage. Moisture stress causes split bulbs.
• 3. Final (75–110 DAT): STOP all irrigation 10–15 days before harvest when 50% tops fall over naturally.

Fertilizer Requirement by Phase:
• Total Dose: 100 kg N : 50 kg P2O5 : 50 kg K2O + 45 kg Sulfur. Basal: 50% N + full P, K & S. Top-dress 50% N at 30 and 45 DAT.

Total Crop Duration:
• Standalone Total Duration: Total Duration: 110–125 days (approximately 3.5 to 4 months) from transplanting to harvest.

Harvesting Details:
• Maturity: 50% neck fall; bulbs develop full skin color.
• Expected Yield: Irrigated Onion: 25–35 tonnes/ha (10–14 t/acre).

Growing Season:
• Kharif: Nursery May–June; Rabi: Nursery Sept–Oct; Late Kharif: Aug–Sept.
"""

# POTATO
DOCS["potato_cultivation_india.txt"] = """Potato Cultivation Guidelines — National Advisory
Source: ICAR-Central Potato Research Institute (CPRI), Shimla

Suitable Agro-Climatic Zones & Recommended Varieties:
• Agro-Climatic Zones: UP (Agra No. 1), WB, Punjab, Gujarat, Karnataka (Hassan, Chikkaballapur).
• Recommended Varieties: Kufri Pukhraj, Kufri Jyoti, Kufri Bahar, Kufri Chipsona-1. Yield: 30–40 tonnes/ha.

Water Requirement by Phase:
• Category: Irrigated Furrow / Drip. Total Water: 500–600 mm.
• 1. Initial (0–25 DAP): Light irrigation at earthing up.
• 2. Middle (25–65 DAP): Tuber Initiation & Bulking (35–55 DAP) is the SINGLE most water-critical stage.
• 3. Final (65–90 DAP): STOP irrigation 10–12 days before haulm cutting.

Fertilizer Requirement by Phase:
• Total Dose: 180 kg N : 100 kg P2O5 : 120 kg K2O. Basal: 50% N + full P & K. Top-dress 50% N at earthing up (30 DAP).

Total Crop Duration:
• Standalone Total Duration: Total Duration: 90–110 days (approximately 3 to 3.5 months) from tuber planting to harvest.

Harvesting Details:
• Maturity: Vines yellow and dry; skin hardens on tuber.
• Expected Yield: 30–40 tonnes/ha (12–16 t/acre).

Growing Season:
• Rabi Season: Planting Oct 15 to Nov 15.
"""

# BRINJAL, CHILLI, OKRA, CABBAGE, CAULIFLOWER
DOCS["brinjal_chilli_okra_cabbage_cauliflower.txt"] = """Vegetable Crops Guidelines — Brinjal, Chilli, Okra, Cabbage & Cauliflower
Source: ICAR-IIHR Bengaluru; TNAU & IARI New Delhi

Suitable Agro-Climatic Zones & Varieties:
• Brinjal: Arka Anand. Chilli: Byadgi Dabbi, Arka Meghana. Okra: Arka Anamika. Cabbage: Golden Acre. Cauliflower: Pusa Snowball.

Water Requirement by Phase:
• Irrigated Vegetable Crops.
• Critical Stages: Flowering & Fruit Development (Chilli/Brinjal 40–60 DAT); Head/Curd Formation (Cole crops 35–50 DAT).
• STOP Irrigation: 5–7 days before harvest.

Fertilizer Requirement by Phase:
• Chilli/Brinjal: 150 kg N : 75 kg P2O5 : 75 kg K2O (split basal, 30, 50 DAT).
• Cabbage/Cauliflower: 150 kg N : 80 kg P2O5 : 100 kg K2O + 15 kg Borax.

Total Crop Duration:
• Standalone Total Duration: Total Duration: Okra 90 days; Brinjal/Chilli 150–180 days (multiple pickings); Cabbage/Cauliflower 75–90 days.

Harvesting Details:
• Maturity: Chilli (green 60 DAT, dry red 120 DAT); Cabbage (firm compact head); Cauliflower (compact white curd).
• Expected Yield: Brinjal 40–50 t/ha; Chilli 15–25 q/ha dry; Okra 12–18 t/ha; Cabbage 35–45 t/ha.

Growing Season:
• Kharif: June–July; Rabi: Oct–Nov; Summer: Jan–Feb.
"""

# PLANTATION CROPS
DOCS["plantation_crops_coffee_tea_coconut_arecanut.txt"] = """Plantation Crops Guidelines — Coffee, Tea, Coconut, Arecanut & Cashew
Source: ICAR-CPCRI Kasaragod; CCRI Kodagu & UPASI

Suitable Agro-Climatic Zones & Varieties:
• Coffee: Arabica Sln 795, Robusta CxR (Kodagu KA). Coconut: West Coast Tall. Arecanut: Mangala, Sumangala (Shimoga KA). Tea: TV-1. Cashew: Vengurla-4.

Water Requirement by Phase:
• Drip / Sprinkler Irrigated.
• SINGLE Most Critical Stage: Coffee Blossom Irrigation (March 25 mm sprinkler water is MANDATORY for uniform flowering). Coconut: Drip 80–100 L/palm/day in summer. Arecanut: Drip 20–25 L/palm/day.

Fertilizer Requirement by Phase:
• Coffee: 140 kg N : 95 kg P2O5 : 140 kg K2O/ha split in May, Sept, Nov.
• Coconut: 500 g N : 320 g P2O5 : 1,200 g K2O/palm/year.
• Arecanut: 100 g N : 40 g P2O5 : 140 g K2O/palm/year.

Total Crop Duration:
• Standalone Total Duration: Total Duration: Perennial Plantation Crops (Bearing starts 3–7 years after planting; yield continues for 40–60+ years). Annual harvest cycle 12 months.

Harvesting Details:
• Maturity: Coffee ripe red cherries Nov–Jan; Coconut ripe nuts every 45 days; Arecanut ripe yellow/red nuts Oct–Dec.
• Expected Yield: Coffee: 1.0–1.5 t/ha; Coconut: 80–120 nuts/palm/yr; Arecanut: 3.0–3.5 kg dry nut/palm/yr.

Growing Season:
• Planting Window: Monsoon onset June to September.
"""

# Write batch 3 to disk
for filename, content in DOCS.items():
    kp_path = os.path.join(KP_DIR, filename)
    ds_path = os.path.join(DS_DIR, filename)
    with open(kp_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    with open(ds_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

print(f"Successfully updated batch 3 crop docs ({len(DOCS)} files).")
