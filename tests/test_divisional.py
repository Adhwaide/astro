"""
tests/test_divisional.py
──────────────────────────
Verifies divisional chart calculations.

Test chart: Kochi, Kerala — 2004-02-28 — 01:15 IST

Run with:
    python tests/test_divisional.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.divisional import calculate_divisional, _d9_navamsha
from app.core.calculator import SIGN_NAMES

DOB   = "2004-02-28"
TOB   = "01:15"
PLACE = "Kochi, Kerala, India"


def test_divisional_charts():
    print(f"\n{'='*60}")
    print(f"  DIVISIONAL CHARTS — VERIFICATION TEST")
    print(f"  Birth: {DOB} {TOB} IST | {PLACE}")
    print(f"{'='*60}\n")

    all_pass = True

    # ── 1. D1 passthrough ────────────────────────────────────────────────────
    d1 = calculate_divisional(DOB, TOB, PLACE, "D1")
    d1_ok = d1["lagna"]["sign_name"] == "Vrischika"
    status = "OK" if d1_ok else "FAIL"
    print(f"  D1 Lagna       : {d1['lagna']['sign_name']}  [{status}]")
    if not d1_ok:
        all_pass = False

    # ── 2. D9 Navamsha basic structure ───────────────────────────────────────
    d9 = calculate_divisional(DOB, TOB, PLACE, "D9")
    d9_planets = len(d9["planets"])
    d9_ok = d9_planets == 9  # 8 planets + Ketu
    status = "OK" if d9_ok else "FAIL"
    print(f"  D9 planet count: {d9_planets}  [{status}]")
    if not d9_ok:
        all_pass = False

    d9_lagna = d9["lagna"]["sign_name"]
    print(f"  D9 Lagna       : {d9_lagna}")

    d9_houses = len(d9["houses"])
    d9h_ok = d9_houses == 12
    status = "OK" if d9h_ok else "FAIL"
    print(f"  D9 house count : {d9_houses}  [{status}]")
    if not d9h_ok:
        all_pass = False

    # ── 3. D9 Navamsha formula verification ──────────────────────────────────
    # Verify the navamsha formula manually for known inputs:
    # Fire sign (Mesha=0), 15° → division 4 → Simha(4)
    nav_test = _d9_navamsha(0, 15.0)
    nav_ok = nav_test == 4
    status = "OK" if nav_ok else "FAIL"
    print(f"  D9(Mesha,15°)  : {SIGN_NAMES[nav_test]} (expected Simha)  [{status}]")
    if not nav_ok:
        all_pass = False

    # Earth sign (Vrishabha=1), 10° → div 3 → Makara offset 9+3=12→0=Mesha
    nav_test2 = _d9_navamsha(1, 10.0)
    nav_ok2 = nav_test2 == 0
    status = "OK" if nav_ok2 else "FAIL"
    print(f"  D9(Vrish,10°)  : {SIGN_NAMES[nav_test2]} (expected Mesha)  [{status}]")
    if not nav_ok2:
        all_pass = False

    # ── 4. D2 Hora structure check ───────────────────────────────────────────
    d2 = calculate_divisional(DOB, TOB, PLACE, "D2")
    d2_ok = d2["lagna"]["sign"] in [3, 4]  # Cancer(3) or Leo(4) only
    status = "OK" if d2_ok else "FAIL"
    print(f"  D2 Lagna       : {d2['lagna']['sign_name']} (must be Cancer/Leo)  [{status}]")
    if not d2_ok:
        all_pass = False

    # All D2 planets must be in Cancer or Leo
    d2_signs_ok = all(p["sign"] in [3, 4] for p in d2["planets"])
    status = "OK" if d2_signs_ok else "FAIL"
    print(f"  D2 all Cancer/Leo: {d2_signs_ok}  [{status}]")
    if not d2_signs_ok:
        all_pass = False

    # ── 5. D10 Dasamsa structure ─────────────────────────────────────────────
    d10 = calculate_divisional(DOB, TOB, PLACE, "D10")
    d10_ok = len(d10["planets"]) == 9
    status = "OK" if d10_ok else "FAIL"
    print(f"  D10 planet count: {len(d10['planets'])}  [{status}]")
    if not d10_ok:
        all_pass = False
    print(f"  D10 Lagna      : {d10['lagna']['sign_name']}")

    # ── 6. D30 Trimsamsa structure ───────────────────────────────────────────
    d30 = calculate_divisional(DOB, TOB, PLACE, "D30")
    d30_ok = len(d30["planets"]) == 9
    status = "OK" if d30_ok else "FAIL"
    print(f"  D30 planet count: {len(d30['planets'])}  [{status}]")
    if not d30_ok:
        all_pass = False
    # D30 only uses 5 signs (Ma=0, Sa=10, Ju=8, Me=2, Ve=6)
    valid_d30 = {0, 2, 6, 8, 10}
    d30_signs_ok = all(p["sign"] in valid_d30 for p in d30["planets"])
    status = "OK" if d30_signs_ok else "FAIL"
    print(f"  D30 valid signs: {d30_signs_ok}  [{status}]")
    if not d30_signs_ok:
        for p in d30["planets"]:
            if p["sign"] not in valid_d30:
                print(f"       {p['name']} in {p['sign_name']}({p['sign']}) — unexpected!")
        all_pass = False

    # ── 7. Print D9 chart ────────────────────────────────────────────────────
    print(f"\n  {'ID':<5} {'Name':<10} {'D1 Sign':<15} {'D9 Sign':<15} {'House':>5}")
    print(f"  {'-'*5} {'-'*10} {'-'*15} {'-'*15} {'-'*5}")
    d1_by_id = {p["id"]: p for p in d1["planets"]}
    for p in d9["planets"]:
        d1p = d1_by_id.get(p["id"], {})
        print(f"  {p['id']:<5} {p['name']:<10} {d1p.get('sign_name','?'):<15} {p['sign_name']:<15} {p['house']:>5}")

    # ── Final verdict ────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    if all_pass:
        print("  RESULT : ALL DIVISIONAL CHECKS PASSED ✓")
    else:
        print("  RESULT : SOME CHECKS FAILED — Review above")
    print(f"{'='*60}\n")

    assert all_pass, "Divisional verification failed"


if __name__ == "__main__":
    test_divisional_charts()
