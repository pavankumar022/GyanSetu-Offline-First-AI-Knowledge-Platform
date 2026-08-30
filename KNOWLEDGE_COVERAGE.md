# GyanSetu Knowledge Base Coverage & Index (v5.0 — 5-Section Standard)

**100% Local · Grounded Verification · Zero Hallucination Baseline**

This document details all topics, crops, government schemes, healthcare protocols, soil/pest management methods, and legal rights physically present and indexed in the GyanSetu local knowledge database.

---

## 🌾 1. Agricultural Crops (41 Major Indian Crops across 7 Sub-Categories)

Every crop document in GyanSetu strictly enforces the **5-Section Standardized Schema**:
1. **`Water Requirement by Phase`**: Initial (germination), Middle (vegetative/flowering critical stage), Final (maturity & stop-irrigation timing), total mm water requirement, Irrigated vs Rainfed classification.
2. **`Fertilizer Requirement by Phase`**: Basal dose (at sowing), Top-Dressing rounds (exact DAS timing & NPK kg/ha), Late-stage foliar sprays, Irrigated vs Rainfed split schedules.
3. **`Total Crop Duration`**: Standalone explicit duration figure (`Total Duration: X-Y days / X-Y months`) with variety/condition breakdown.
4. **`Harvesting Details`**: Visual/physical maturity indicators, harvesting method (manual/mechanical), post-harvest handling & drying moisture %, self-contained expected yield.
5. **`Growing Season`**: Season tags (Kharif / Rabi / Zaid / Perennial) and region-specific sowing windows.

| Category | Crop Name | Primary Source File | Agro-Climatic Coverage | Standardized 5-Section Coverage |
|---|---|---|---|---|
| **Cereals** | Wheat | `wheat_cultivation_karnataka.txt`, `wheat_cultivation_india.txt` | Indo-Gangetic Plains, MP, KA (Belagavi, Dharwad) | ✅ Water (CRI 20-25 DAS), Fertilizer (120:60:40), Duration (110-135d), Harvest, Season (Rabi) |
| **Cereals** | Rice (Paddy) | `rice_cultivation_karnataka.txt`, `rice_cultivation_india.txt` | Mandya, Raichur, Coastal KA, WB, UP, AP | ✅ Water (Panicle 50-65 DAS), Fertilizer (100:50:50), Duration (120-140d), Harvest, Season (Kharif/Rabi) |
| **Cereals** | Maize (Corn) | `maize_cultivation_karnataka.txt` | Davanagere, Haveri, Belagavi, MP, Bihar | ✅ Water (Silking 45-60 DAS), Fertilizer (150:75:40), Duration (100-120d), Harvest, Season (Kharif/Rabi) |
| **Cereals** | Ragi (Finger Millet) | `ragi_cultivation_karnataka.txt` | Tumakuru, Kolar, Hassan, Mandya, TN | ✅ Water (Earhead 45-55 DAS), Fertilizer (100:50:50), Duration (100-115d), Harvest, Season (Kharif/Summer) |
| **Cereals** | Barley | `barley_cultivation_india.txt` | Rajasthan (No.1), UP, MP, Haryana, Punjab | ✅ Water (CRI 25-30 DAS), Fertilizer (60:30:20), Duration (110-125d), Harvest, Season (Rabi) |
| **Cereals** | Jowar (Sorghum) | `millet_bajra_jowar_india.txt` | Solapur/Kalaburagi dryland belt, MH, KA | ✅ Water (Boot stage 45-55 DAS), Fertilizer (80:40:40), Duration (80-100d), Harvest, Season (Kharif/Rabi) |
| **Cereals** | Bajra (Pearl Millet) | `millet_bajra_jowar_india.txt` | Rajasthan (No.1), Gujarat, Northern Dry KA | ✅ Water (Boot stage 45-55 DAS), Fertilizer (80:40:40), Duration (80-100d), Harvest, Season (Kharif) |
| **Pulses** | Chickpea (Gram/Chana) | `chickpea_gram_india.txt` | MP (No.1), MH, Kalaburagi, Rajasthan | ✅ Water (Pre-flowering 45 DAS), Fertilizer (20:50:20+S), Duration (100-115d), Harvest, Season (Rabi) |
| **Pulses** | Tur (Pigeon Pea) | `pigeon_pea_cultivation_india.txt` | Kalaburagi Red Gram bowl, MP, MH | ✅ Water (Flower initiation 105-115 DAS), Fertilizer (25:50:25+S), Duration (150-180d), Harvest, Season (Kharif) |
| **Pulses** | Green Gram (Moong) | `moong_urad_lentil_pulses.txt` | MP, Rajasthan, UP, KA Rice Fallows | ✅ Water (Flowering 30-45 DAS), Fertilizer (20:40:20+S), Duration (65-75d), Harvest, Season (Kharif/Summer) |
| **Pulses** | Black Gram (Urad) | `moong_urad_lentil_pulses.txt` | AP, KA, MH, Rice Fallows | ✅ Water (Flowering 30-45 DAS), Fertilizer (20:40:20+S), Duration (65-75d), Harvest, Season (Kharif/Rabi) |
| **Pulses** | Lentil (Masoor) | `moong_urad_lentil_pulses.txt` | UP, MP, Bihar, West Bengal | ✅ Water (Flowering 40 DAS), Fertilizer (20:40:20+S), Duration (110-120d), Harvest, Season (Rabi) |
| **Oilseeds** | Groundnut (Peanut) | `groundnut_cultivation_india.txt` | Chitradurga, Tumakuru, Gujarat, Anantapur | ✅ Water (Pegging 35-50 DAS), Fertilizer (25:50:25+Gypsum), Duration (100-115d), Harvest, Season (Kharif/Summer) |
| **Oilseeds** | Sunflower | `sunflower_cultivation_india.txt` | Vijayapura, Koppal, Raichur, Bellary | ✅ Water (Seed setting 45-65 DAS), Fertilizer (60:60:30+Boron), Duration (90-105d), Harvest, Season (Kharif/Rabi/Summer) |
| **Oilseeds** | Mustard & Rapeseed | `mustard_rapeseed_india.txt` | Rajasthan (No.1), MP, Haryana, UP | ✅ Water (Rosette 30-35 DAS), Fertilizer (80:40:40+S), Duration (105-125d), Harvest, Season (Rabi) |
| **Oilseeds** | Soybean | `soybean_cultivation_india.txt` | MP Malwa, Latur, Belagavi, Bidar | ✅ Water (Pod filling 40-65 DAS), Fertilizer (30:60:30+S), Duration (90-105d), Harvest, Season (Kharif) |
| **Oilseeds** | Sesame (Til) | `sesame_castor_oilseeds.txt` | Gujarat, Rajasthan, MP, WB, KA | ✅ Water (Flowering 30 DAS), Fertilizer (40:20:20+S), Duration (80-90d), Harvest, Season (Kharif/Summer) |
| **Oilseeds** | Castor | `sesame_castor_oilseeds.txt` | Gujarat (No.1), KA (Raichur), AP | ✅ Water (Main spike 45 DAS), Fertilizer (80:40:30 split), Duration (150-180d), Harvest, Season (Kharif/Rabi) |
| **Cash Crops** | Cotton | `cotton_cultivation_india.txt` | Dharwad hub, Gujarat, MH, Telangana | ✅ Water (Peak boll 60-90 DAS), Fertilizer (150:75:75+Mg), Duration (150-180d), Harvest, Season (Kharif) |
| **Cash Crops** | Sugarcane | `sugarcane_cultivation_india.txt` | Belagavi, Mandya, MH, UP, TN | ✅ Water (Formative 45-120 DAP), Fertilizer (250:75:75), Duration (360-540d), Harvest, Season (Adsali/Suru) |
| **Cash Crops** | Jute | `jute_tobacco_cash_crops.txt` | West Bengal (Hooghly/Nadia), Assam | ✅ Water (Grand growth 45-60 Days), Fertilizer (80:40:40), Duration (120d), Harvest, Season (Pre-monsoon) |
| **Cash Crops** | Tobacco | `jute_tobacco_cash_crops.txt` | AP (Guntur), KA (Mysuru FCV), Gujarat | ✅ Water (Topping stage 45-60 Days), Fertilizer (40:60:120 non-chloride K), Duration (120-140d), Harvest, Season (Rabi) |
| **Fruits** | Banana | `banana_cultivation_india.txt` | AP, Jalgaon, Tamil Nadu, Mysuru | ✅ Water (Bunch emergence 6-7 MAP), Fertilizer (200:50:300 g/plant), Duration (330-365d), Harvest, Season (June-Aug) |
| **Fruits** | Mango | `mango_papaya_grapes_pomegranate_citrus.txt` | UP, MH, AP, KA (Alphonso, Badami) | ✅ Water (Fruit set Feb-Mar), Fertilizer (1000:500:1000 g/tree), Duration (110-120d from fruit set), Harvest, Season (June-Aug) |
| **Fruits** | Papaya | `mango_papaya_grapes_pomegranate_citrus.txt` | MP, Gujarat, MH, KA | ✅ Water (Flowering 4 MAP), Fertilizer (250:250:500 g/plant), Duration (9-10 months), Harvest, Season (Feb-Mar / June-July) |
| **Fruits** | Grapes | `mango_papaya_grapes_pomegranate_citrus.txt` | MH (Nashik), KA (Vijayapura, Chikkaballapur) | ✅ Water (Fruit set Oct-Nov), Fertilizer (500:300:800 kg/ha), Duration (135-150d post pruning), Harvest, Season (Oct pruning) |
| **Fruits** | Pomegranate | `mango_papaya_grapes_pomegranate_citrus.txt` | MH (Solapur), KA (Koppal, Vijayapura) | ✅ Water (Bahar flowering stress), Fertilizer (625:250:500 g/tree), Duration (150-180d post Bahar), Harvest, Season (June-July) |
| **Fruits** | Citrus (Lime/Mosambi) | `mango_papaya_grapes_pomegranate_citrus.txt` | MH (Nagpur), AP, KA (Vijayapura) | ✅ Water (Fruit development), Fertilizer (600:200:300 g/tree), Duration (8-9 months), Harvest, Season (June-Aug) |
| **Vegetables** | Tomato | `tomato_cultivation_india.txt` | Kolar hub, Chikkaballapur, AP, MP | ✅ Water (Flowering 30-50 DAT), Fertilizer (180:120:150), Duration (110-130d), Harvest, Season (Kharif/Rabi/Summer) |
| **Vegetables** | Onion | `onion_cultivation_india.txt` | Nashik, Ahmednagar, Vijayapura, Gadag | ✅ Water (Bulb development 45-65 DAT), Fertilizer (100:50:50+S), Duration (110-125d), Harvest, Season (Kharif/Rabi) |
| **Vegetables** | Potato | `potato_cultivation_india.txt` | UP Agra, West Bengal, Gujarat, Hassan | ✅ Water (Tuber bulking 35-55 DAP), Fertilizer (180:100:120), Duration (90-110d), Harvest, Season (Rabi) |
| **Vegetables** | Brinjal (Eggplant) | `brinjal_chilli_okra_cabbage_cauliflower.txt` | AP, KA (Belagavi), West Bengal, Odisha | ✅ Water (Fruit development 40-60 DAT), Fertilizer (150:75:75), Duration (150-180d), Harvest, Season (Kharif/Rabi) |
| **Vegetables** | Chilli | `brinjal_chilli_okra_cabbage_cauliflower.txt` | AP (Guntur), KA (Byadgi GI chilli) | ✅ Water (Flowering 40-60 DAT), Fertilizer (150:75:75), Duration (150-180d), Harvest, Season (Kharif/Rabi) |
| **Vegetables** | Okra (Bhindi) | `brinjal_chilli_okra_cabbage_cauliflower.txt` | Gujarat, MH, AP, KA, UP, Bihar | ✅ Water (Flowering 30-45 DAS), Fertilizer (100:50:50), Duration (90d), Harvest, Season (Kharif/Summer) |
| **Vegetables** | Cabbage & Cauliflower | `brinjal_chilli_okra_cabbage_cauliflower.txt` | WB, Bihar, UP, KA (Belagavi) | ✅ Water (Head/Curd formation 35-50 DAT), Fertilizer (150:80:100+Borax), Duration (75-90d), Harvest, Season (Rabi/Kharif) |
| **Plantation** | Coffee | `plantation_crops_coffee_tea_coconut_arecanut.txt` | KA (Kodagu, Chikkamagaluru, Hassan >70%) | ✅ Water (Blossom March sprinkler), Fertilizer (140:95:140), Duration (Perennial 12m cycle), Harvest, Season (June-Sept) |
| **Plantation** | Tea | `plantation_crops_coffee_tea_coconut_arecanut.txt` | Assam, WB (Darjeeling), TN Nilgiris | ✅ Water (Flushing wet season), Fertilizer (150:50:100), Duration (Perennial), Harvest, Season (June-Sept) |
| **Plantation** | Coconut | `plantation_crops_coffee_tea_coconut_arecanut.txt` | Kerala, KA (Tumakuru, Hassan), TN | ✅ Water (Drip 80-100 L/palm/day), Fertilizer (500:320:1200 g/palm), Duration (Perennial 60+ yrs), Harvest, Season (June-Sept) |
| **Plantation** | Arecanut (Betelnut) | `plantation_crops_coffee_tea_coconut_arecanut.txt` | KA (Shimoga, Chikkamagaluru, Dakshina Kannada) | ✅ Water (Drip 20-25 L/palm/day), Fertilizer (100:40:140 g/palm), Duration (Perennial 40+ yrs), Harvest, Season (May-June) |
| **Plantation** | Cashew | `plantation_crops_coffee_tea_coconut_arecanut.txt` | MH (Konkan), AP, KA (Dakshina Kannada) | ✅ Water (Drip 30 L/tree flowering), Fertilizer (500:125:125 g/tree), Duration (Perennial), Harvest, Season (June-Aug) |

---

## 🏛️ 2. Government Schemes & Subsidies (National & Karnataka)

| Scheme Name | Primary Source File | Target Beneficiaries | Key Benefits & Subsidies |
|---|---|---|---|
| **PM-KISAN** | `agricultural_subsidies.txt` | All landholding farmer families | ₹6,000/year income support in 3 equal installments of ₹2,000 |
| **PMFBY (Crop Insurance)** | `pmfby_crop_insurance.txt` | All loanee & non-loanee farmers | Capped premium (1.5% Rabi, 2.0% Kharif, 5.0% Commercial), 72h localized loss claim |
| **Kisan Credit Card (KCC)** | `kisan_credit_card_kcc.txt` | Farmers, Tenant farmers, Dairy, Fisheries | 7% interest rate, 3% prompt repayment incentive -> **4% net effective interest** |
| **PMKSY (Micro-Irrigation)** | `pmksy_irrigation_subsidy.txt` | Small & marginal farmers | 55% subsidy for Drip & Sprinkler (up to 90% in Karnataka top-up), 50% solar pump |
| **Soil Health Card (SHC)** | `soil_health_card_scheme.txt` | All landholders | Free soil test report every 2 years, 12 parameter breakdown, Lime/Gypsum dosage |
| **Karnataka State Schemes** | `karnataka_state_schemes.txt` | KA farmers & children | Raitha Vidya Nidhi (₹2k-₹11k student scholarship), Krishi Bhagya 90% farm pond, Yashasvini ₹5L health cover |
| **Raitha Siri (Millet Scheme)** | `karnataka_raitha_siri_bhoochetana.txt` | Karnataka millet farmers | ₹10,000/hectare Direct Benefit Transfer (DBT) incentive for millet cultivation |
| **Bhoochetana Soil Scheme** | `karnataka_raitha_siri_bhoochetana.txt` | Dryland farmers in Karnataka | 50% subsidy on Micronutrients (Zinc, Borax, Gypsum) and Bio-fertilizers |
| **e-NAM Agri Marketing** | `karnataka_raitha_siri_bhoochetana.txt` | All farmers selling produce | Transparent online APMC mandi bidding, direct 24h bank payment, free quality assaying |
| **SMAM & NFSM** | `agricultural_subsidies.txt` | Farmers & SHGs | 40-50% mechanization subsidy (tractors, harvesters), 50% certified seed subsidy |

---

## 🏥 3. Rural Healthcare & Medical Protocols

| Topic / Protocol | Primary Source File | Target Caregivers | Clinical Protocol / Guidelines |
|---|---|---|---|
| **Infant Immunization (NIS)** | `infant_immunization_schedule.txt` | ANMs, ASHA workers, Nurses | Birth (BCG, OPV0, HepB), 6-10-14w (Pentavalent, RVV, fIPV, PCV), 9-12m (MR1, Vit A) |
| **ASHA Maternal Guidelines** | `asha_maternal_health_guidelines.txt` | ASHA workers, ANMs | 4 mandatory ANC visits, IFA red tablets, 8 High-Risk Pregnancy danger signs, JSY ₹1400 cash incentive |
| **Rural First Aid Emergencies** | `rural_first_aid_emergencies.txt` | Community Health Officers | Snake Bite (RIGHT protocol, ASV 108), Heat Stroke (cold water immersion), Burns, Fracture splinting |
| **Dehydration & WHO ORS** | `dehydration_ors_protocol.txt` | Parents, Healthcare workers | WHO Reduced Osmolarity ORS 1L preparation, 14-day continuous Zinc supplementation (10-20 mg/day) |
| **PHC Referral Symptoms** | `phc_referral_symptoms.txt` | Rural health workers | Malaria (RDT/ACT), Dengue shock signs, TB Nikshay 2w cough screening, Pneumonia fast breathing |
| **Child Malnutrition & Anemia** | `child_malnutrition_anemia_prevention.txt` | Anganwadi workers, ASHA | MUAC <11.5 cm SAM referral to NRC, Anemia Mukt Bharat weekly IFA syrup/tablet, Albendazole deworming |

---

## 🧪 4. Soil Health & Integrated Pest Management

| Topic / Protocol | Primary Source File | Category | Detailed Guidance |
|---|---|---|---|
| **Organic Pest Control** | `organic_pest_control_methods.txt` | Non-chemical farming | NSKE 5%, Agniastra, Jeevamrutha, Panchagavya, Yellow/Blue sticky traps, Trichogramma cards |
| **Integrated Pest Management** | `integrated_pest_management_ipm.txt` | Plant Protection | ETL thresholds for BPH (10/hill), FAW (10% whorl), Pink bollworm (8 moths/trap), Trap cropping |
| **Micronutrient Correction** | `micronutrient_deficiency_guide.txt` | Soil Fertility | Zinc (White Bud/Khaira) ZnSO4 25kg/ha, Boron (Hollow heart) Solubor 0.2%, Iron chlorosis FeSO4 |
| **Soil Health Card Testing** | `soil_health_card_scheme.txt` | Soil Management | 12 parameter soil grid sampling, Lime @ 2-4 q/acre for acidic, Gypsum @ 5 q/acre for alkaline |

---

## ⚖️ 5. Legal Rights & Rural Entitlements

| Entitlement / Area | Primary Source File | Statutory Guarantee | Procedures & Grievances |
|---|---|---|---|
| **MGNREGS Work Guarantee** | `mgnregs_full_guide.txt` | 100 days guaranteed wage work | Equal wages, 15-day job allocation, 25-50% Unemployment Allowance, Ombudsman helpline 1800-11-1555 |
| **Pahani / RTC Land Rights** | `land_records_pahani_rights.txt` | Record of Rights & Crop sown | Bhoomi Portal ₹15 digital download, 30-day Sakala mutation limit, Tatsal boundary survey |
| **Farmer Distress & Legal Aid** | `farmer_distress_legal_aid.txt` | NALSA / DLSA free legal assistance | Free lawyer for small farmers, Kisan Call Centre 1800-180-1551, Tele-MANAS 14416 mental health hotline |
| **Agri Inputs Consumer Rights** | `agri_input_consumer_rights.txt` | Seeds Act 1966 & FCO 1985 | Compensation for failed seeds, mandatory MRP cash memo, Consumer Court (1915 helpline) claims |
