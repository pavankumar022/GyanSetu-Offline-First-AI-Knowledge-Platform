"""
scripts/eval_rag.py — GyanSetu RAG Generalization Eval Harness (v4.0 — Broad Test Set)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tests intent-aware retrieval across all 7 categories:
  1. Crops (Cereals, Pulses, Oilseeds, Cash, Fruits, Vegetables, Plantation)
  2. Seasons (Kharif, Rabi, Zaid)
  3. Water / Irrigation Types (Irrigated vs Rainfed)
  4. Government Schemes (National & Karnataka)
  5. Rural Health (Immunization, ASHA, First Aid, ORS, Malnutrition)
  6. Soil & Pest Management (IPM, Organic, Micronutrient)
  7. Legal Rights (MGNREGS, Pahani, Helplines, Input Consumer Rights)

Run from project root:
    python scripts/eval_rag.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from local_ai.rag_pipeline import query_offline_ai

# Test suite: (question, expected_doc_fragment, expected_subtopic, must_contain, must_not_contain)
TESTS = [
    # ─── CEREALS ─────────────────────────────────────────────────────────────
    ("how often should I water my paddy field", "rice", "irrigation", ["water", "irrigat", "flood", "awd"], ["fertilizer", "npk", "urea"]),
    ("urea dose for rice", "rice", "fertilizer", ["nitrogen", "npk", "kg", "urea"], ["irrigat", "watering", "spacing"]),
    ("best time to plant rice in Karnataka", "rice", "sowing", ["june", "july", "kharif", "dec", "jan", "sowing", "transplant"], ["fertilizer", "npk", "yield"]),
    ("rice row spacing", "rice", "spacing", ["cm", "spacing", "distance"], ["fertilizer", "npk"]),
    ("insects that attack rice", "rice", "pest", ["pest", "insect", "borer", "hopper"], ["fertilizer", "npk", "irrigat"]),
    ("rice fungal disease treatment", "rice", "disease", ["blast", "blight", "fungal", "disease", "spray", "khaira"], ["fertilizer", "npk", "insect"]),
    ("expected rice yield per acre", "rice", "yield", ["yield", "tonne", "quintal", "per hectare"], ["irrigat", "fertilizer"]),

    # ─── MAIZE / CORN ─────────────────────────────────────────────────────────
    ("when do I add urea to my corn crop", "maize", "fertilizer", ["urea", "nitrogen", "top dress"], ["irrigat", "pest", "disease"]),
    ("how much water does maize need", "maize", "irrigation", ["irrigat", "water", "moisture"], ["fertilizer", "npk"]),

    # ─── WHEAT ────────────────────────────────────────────────────────────────
    ("wheat irrigation schedule stages", "wheat", "irrigation", ["irrigat", "cri", "crown root"], ["fertilizer", "npk"]),

    # ─── NEW PULSES (Moong, Urad, Lentil) ─────────────────────────────────────
    ("summer moong irrigation frequency", "moong_urad", "irrigation", ["summer", "irrigat", "flowering", "pod"], ["cotton", "rice", "wheat"]),
    ("urad bean seed rate per hectare", "moong_urad", "spacing", ["kg/ha", "seed rate", "spacing", "15"], ["fertilizer", "npk"]),

    # ─── NEW OILSEEDS (Sesame, Castor) ───────────────────────────────────────
    ("castor plant spacing and seed rate", "sesame_castor", "spacing", ["castor", "spacing", "kg/ha", "cm"], ["fertilizer", "npk"]),
    ("sesame phyllody disease vector spray", "sesame_castor", "disease", ["phyllody", "sesame", "phytoplasma", "leafhopper"], ["fertilizer", "irrigat"]),

    # ─── NEW CASH CROPS (Jute, Tobacco) ──────────────────────────────────────
    ("jute retting water requirement", "jute_tobacco", "irrigation", ["jute", "retting", "water", "harvest"], ["fertilizer", "npk"]),
    ("tobacco potash fertilizer non chloride", "jute_tobacco", "fertilizer", ["potassium", "potash", "tobacco", "sulfate"], ["irrigat", "spacing"]),

    # ─── NEW FRUITS (Mango, Papaya, Grapes, Pomegranate, Citrus) ─────────────
    ("alphonso mango planting spacing high density", "mango_papaya", "spacing", ["mango", "spacing", "m x", "density"], ["fertilizer", "npk"]),
    ("papaya drip irrigation water per day", "mango_papaya", "irrigation", ["papaya", "drip", "litres", "water"], ["fertilizer", "npk"]),
    ("pomegranate bacterial blight teliya treatment", "mango_papaya", "disease", ["pomegranate", "bacterial", "blight", "streptocycline"], ["fertilizer", "irrigat"]),
    ("citrus leaf miner spray", "mango_papaya", "pest", ["citrus", "miner", "spray", "imidacloprid"], ["fertilizer", "irrigat"]),

    # ─── NEW VEGETABLES (Brinjal, Chilli, Okra, Cabbage) ─────────────────────
    ("byadgi chilli thrips control spray", "brinjal_chilli", "pest", ["chilli", "thrips", "fipronil", "spray"], ["fertilizer", "irrigat"]),
    ("brinjal shoot fruit borer spray", "brinjal_chilli", "pest", ["brinjal", "borer", "shoot", "emamectin"], ["fertilizer", "irrigat"]),
    ("cauliflower hollow stem borax treatment", "brinjal_chilli", "fertilizer", ["cauliflower", "borax", "hollow", "stem"], ["irrigat", "pest"]),

    # ─── NEW PLANTATION (Coffee, Tea, Coconut, Arecanut, Cashew) ─────────────
    ("coffee blossom irrigation timing", "plantation_crops", "irrigation", ["coffee", "blossom", "march", "sprinkler"], ["fertilizer", "npk"]),
    ("arecanut koleroga fruit rot bordeaux spray", "plantation_crops", "disease", ["arecanut", "koleroga", "bordeaux", "fruit rot"], ["fertilizer", "irrigat"]),
    ("coconut water requirement drip per day", "plantation_crops", "irrigation", ["coconut", "drip", "litres", "water"], ["fertilizer", "npk"]),

    # ─── SCHEMES (National & KA State) ───────────────────────────────────────
    ("how much premium do I pay for PMFBY crop insurance", "pmfby", "cost", ["premium", "%", "kharif"], ["eligib", "document"]),
    ("what documents do I need to apply for KCC", "kisan_credit_card", "application", ["aadhaar", "land", "pahani"], ["premium", "subsidy"]),
    ("Raitha Siri scheme incentive for millet farmers", "karnataka_raitha_siri", "cost", ["raitha siri", "10,000", "millet", "dbt"], ["pmfby", "kcc"]),

    # ─── RURAL HEALTH ─────────────────────────────────────────────────────────
    ("infant BCG vaccine when is it given", "immunization", "health-protocol", ["bcg", "birth", "vaccine"], ["fertilizer", "crop"]),
    ("MUAC tape red zone child malnutrition referral", "child_malnutrition", "health-protocol", ["muac", "11.5", "sam", "nrc"], ["fertilizer", "crop"]),

    # ─── LEGAL / CONSUMER RIGHTS ──────────────────────────────────────────────
    ("substandard seed germination complaint seed inspector", "agri_input_consumer", "legal-rights", ["seed", "germination", "inspector", "complaint"], ["fertilizer", "irrigat"]),
    ("MGNREGS daily wage rate in Karnataka", "mgnregs", "legal-rights", ["karnataka", "wage", "₹", "349"], ["fertilizer", "crop"]),

    # ─── OUT-OF-SCOPE ─────────────────────────────────────────────────────────
    ("what is the population of Australia", None, None, [], []),
    ("give me a chocolate cake recipe", None, None, [], []),
]


def run_eval():
    print("=" * 70)
    print("  GyanSetu RAG Generalization Eval Harness (v4.0 — Broad)")
    print("=" * 70)

    passed = 0
    failed = 0
    total = len(TESTS)
    failures = []

    for i, test in enumerate(TESTS):
        q, expected_doc, expected_subtopic, must_contain, must_not = test
        result = query_offline_ai(q, top_k=5)
        answer = result.get("answer", "").lower()
        citations = result.get("citations", [])

        # Check 1: Out-of-scope queries
        if expected_doc is None:
            if citations:
                failures.append((q, "FAIL: Out-of-scope query returned citations", citations))
                failed += 1
                continue
            else:
                print(f"[{i+1:02d}] [PASS] OUT-OF-SCOPE (correctly rejected): {q[:60]}")
                passed += 1
                continue

        # Check 2: Confidence >= 75%
        if not citations:
            failures.append((q, "FAIL: No citations (confidence too low or no doc)", []))
            failed += 1
            print(f"[{i+1:02d}] [FAIL] NO CITATION: {q[:60]}")
            continue

        # Check 3: Correct document retrieved
        all_paths = " ".join(c.get("filepath", "") for c in citations).lower()
        doc_ok = expected_doc.lower() in all_paths
        if not doc_ok:
            failures.append((q, f"FAIL: Expected doc '{expected_doc}' not in citations: {all_paths}", citations))
            failed += 1
            print(f"[{i+1:02d}] [FAIL] WRONG DOC (expected={expected_doc}): {q[:60]}")
            print(f"       Got: {all_paths[:100]}")
            continue

        # Check 4: must_contain any
        contains_ok = not must_contain or any(kw in answer for kw in must_contain)
        if not contains_ok:
            failures.append((q, f"FAIL: Answer missing key sub-topic terms {must_contain}", []))
            failed += 1
            print(f"[{i+1:02d}] [FAIL] WRONG SUBTOPIC (expected any of {must_contain[:3]}): {q[:60]}")
            print(f"       Answer start: {answer[:150]}")
            continue

        # Check 5: must_not_contain
        bleed_terms = [kw for kw in must_not if kw in answer]
        if bleed_terms:
            print(f"[{i+1:02d}] [WARN-BLEED] ({bleed_terms}): {q[:60]}")

        print(f"[{i+1:02d}] [PASS] doc={expected_doc}, conf={citations[0]['confidence']}%: {q[:60]}")
        passed += 1

    print()
    print("=" * 70)
    print(f"  Results: {passed}/{total} passed, {failed} failed")
    print("=" * 70)

    if failures:
        print("\nFailed tests:")
        for q, reason, citations in failures:
            print(f"  [FAIL] [{q[:55]}]: {reason[:80]}")

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_eval()
    sys.exit(0 if failed == 0 else 1)
