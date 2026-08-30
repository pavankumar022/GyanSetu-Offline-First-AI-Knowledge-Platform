"""
scripts/eval_rag.py — GyanSetu RAG Generalization Eval Harness (v5.0 — 5-Section Standard)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tests intent-aware retrieval across all five standardized sections:
  1. Water Requirement by Phase ("how much water", "stop watering", "critical stage")
  2. Fertilizer Requirement by Phase ("basal dose", "top dressing schedule")
  3. Total Crop Duration ("how many months", "total crop duration")
  4. Harvesting Details ("ready to harvest", "signs of maturity")
  5. Growing Season ("which season", "sowing window")

Run from project root:
    python scripts/eval_rag.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from local_ai.rag_pipeline import query_offline_ai

TESTS = [
    # ─── SECTION A: WATER REQUIREMENT BY PHASE ────────────────────────────────
    ("how much water does maize need in the flowering stage", "maize", "irrigation", ["silking", "critical", "water"], ["fertilizer", "npk"]),
    ("when should I stop watering wheat before harvest", "wheat", "irrigation", ["stop", "10", "15", "harvest", "dough"], ["fertilizer", "npk"]),
    ("coffee blossom irrigation timing", "plantation_crops", "irrigation", ["coffee", "blossom", "march", "sprinkler"], ["fertilizer", "npk"]),
    ("papaya drip irrigation water per day", "mango_papaya", "irrigation", ["papaya", "drip", "litres"], ["fertilizer", "npk"]),

    # ─── SECTION B: FERTILIZER REQUIREMENT BY PHASE ───────────────────────────
    ("fertilizer dose for rice at sowing time", "rice", "fertilizer", ["basal", "50%", "100%", "npk", "puddling"], ["harvest", "yield"]),
    ("top dressing schedule for sugarcane", "sugarcane", "fertilizer", ["tillering", "90", "earthing", "nitrogen"], ["harvest", "brix"]),
    ("cauliflower hollow stem borax treatment", "brinjal_chilli", "fertilizer", ["cauliflower", "borax", "hollow", "stem"], ["irrigat", "pest"]),
    ("tobacco potash fertilizer non chloride", "jute_tobacco", "fertilizer", ["potassium", "potash", "tobacco", "sulfate"], ["irrigat"]),

    # ─── SECTION C: TOTAL CROP DURATION ───────────────────────────────────────
    ("how many months does tur take to grow", "pigeon_pea", "duration", ["150", "180", "months", "duration"], ["fertilizer", "npk"]),
    ("how long does ragi take to reach harvest", "ragi", "duration", ["100", "115", "days", "duration"], ["fertilizer", "npk"]),
    ("total crop duration for cotton", "cotton", "duration", ["150", "180", "days", "months"], ["fertilizer", "npk"]),

    # ─── SECTION D: HARVESTING DETAILS ────────────────────────────────────────
    ("when is groundnut ready to harvest", "groundnut", "harvest", ["yellow", "inside", "dark", "brown", "pods"], ["fertilizer", "npk"]),
    ("signs that sunflower is ready for harvest", "sunflower", "harvest", ["lemon", "yellow", "back", "head", "florets"], ["fertilizer", "npk"]),
    ("how to harvest jute for fibre", "jute_tobacco", "harvest", ["flowering", "retting", "harvest", "fibre"], ["fertilizer", "npk"]),

    # ─── SECTION E: GROWING SEASON ────────────────────────────────────────────
    ("which season should I grow chickpea in", "chickpea", "season", ["rabi", "october", "winter", "sowing"], ["fertilizer", "npk"]),
    ("sowing window for mustard in Rajasthan", "mustard", "season", ["october", "rabi", "sowing"], ["fertilizer", "npk"]),
    ("Raitha Siri scheme incentive for millet farmers", "karnataka_raitha_siri", "cost", ["raitha siri", "10,000", "millet", "dbt"], ["pmfby", "kcc"]),

    # ─── RURAL HEALTH & LEGAL ─────────────────────────────────────────────────
    ("infant BCG vaccine when is it given", "immunization", "health-protocol", ["bcg", "birth", "vaccine"], ["fertilizer", "crop"]),
    ("MUAC tape red zone child malnutrition referral", "child_malnutrition", "health-protocol", ["muac", "11.5", "sam", "nrc"], ["fertilizer", "crop"]),
    ("MGNREGS daily wage rate in Karnataka", "mgnregs", "legal-rights", ["karnataka", "wage", "₹", "349"], ["fertilizer", "crop"]),

    # ─── OUT-OF-SCOPE ─────────────────────────────────────────────────────────
    ("what is the population of Australia", None, None, [], []),
    ("give me a chocolate cake recipe", None, None, [], []),
]


def run_eval():
    print("=" * 70)
    print("  GyanSetu RAG Generalization Eval Harness (v5.0 — 5-Section Standard)")
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
