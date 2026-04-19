"""
tests/test_dashas.py
─────────────────────
Verifies Vimshottari Dasha engine against a known chart.

Test chart: Kochi, Kerala — 2004-02-28 — 01:15 IST
Moon is in Rohini (nakshatra index 3) → ruled by Moon
Expected starting Mahadasha lord: Moon (Mo)

Run with:
    python tests/test_dashas.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.dashas import calculate_dasha, _moon_dasha_balance, DASHA_YEARS, TOTAL_YEARS

# ── Known birth data ──────────────────────────────────────────────────────────
DOB   = "2004-02-28"
TOB   = "01:15"
PLACE = "Kochi, Kerala, India"


def test_dasha_engine():
    print(f"\n{'='*60}")
    print(f"  VIMSHOTTARI DASHA — VERIFICATION TEST")
    print(f"  Birth: {DOB} {TOB} IST | {PLACE}")
    print(f"{'='*60}\n")

    result = calculate_dasha(DOB, TOB, PLACE)
    all_pass = True

    # ── 1. Moon nakshatra check ──────────────────────────────────────────────
    moon_nak = result["moon_nakshatra"]
    nak_ok = moon_nak == "Rohini"
    status = "OK" if nak_ok else "FAIL"
    print(f"  Moon Nakshatra : {moon_nak}  [{status}]")
    if not nak_ok:
        print(f"       Expected  : Rohini")
        all_pass = False

    # ── 2. Starting lord check ───────────────────────────────────────────────
    start = result["starting_lord"]
    lord_ok = start == "Mo"
    status = "OK" if lord_ok else "FAIL"
    print(f"  Starting Lord  : {result['starting_lord_name']} ({start})  [{status}]")
    if not lord_ok:
        print(f"       Expected  : Mo (Chandra)")
        all_pass = False

    # ── 3. Balance sanity check ──────────────────────────────────────────────
    balance = result["balance_at_birth_years"]
    balance_ok = 0.0 < balance <= 10.0  # Moon dasha = 10 years max
    status = "OK" if balance_ok else "FAIL"
    print(f"  Balance (yrs)  : {balance:.4f}  [{status}]")
    if not balance_ok:
        print(f"       Expected  : between 0 and 10 years")
        all_pass = False

    # ── 4. Mahadasha count = 9 ───────────────────────────────────────────────
    maha_count = len(result["mahadasha"])
    count_ok = maha_count == 9
    status = "OK" if count_ok else "FAIL"
    print(f"  Maha count     : {maha_count}  [{status}]")
    if not count_ok:
        all_pass = False

    # ── 5. Total years = balance + remaining 8 full dashas ─────────────────
    #    The 120-year cycle starts BEFORE birth. From birth onward,
    #    total = balance + sum of remaining 8 full Mahadashas.
    total = sum(m["duration_years"] for m in result["mahadasha"])
    first_lord = result["starting_lord"]
    from app.core.dashas import DASHA_YEARS as DY
    expected_total = balance + (120.0 - DY[first_lord])
    total_ok = abs(total - expected_total) < 0.01
    status = "OK" if total_ok else "FAIL"
    print(f"  Total years    : {total:.4f} (expected {expected_total:.4f})  [{status}]")
    if not total_ok:
        print(f"       Expected  : ~{expected_total:.4f}")
        all_pass = False

    # ── 6. Mahadasha sequence (should follow Vimshottari from Moon) ──────────
    expected_seq = ["Mo", "Ma", "Ra", "Ju", "Sa", "Me", "Ke", "Ve", "Su"]
    actual_seq = [m["lord"] for m in result["mahadasha"]]
    seq_ok = actual_seq == expected_seq
    status = "OK" if seq_ok else "FAIL"
    print(f"  Maha sequence  : {' -> '.join(actual_seq)}  [{status}]")
    if not seq_ok:
        print(f"       Expected  : {' -> '.join(expected_seq)}")
        all_pass = False

    # ── 7. Each Mahadasha has 9 Antardashas ──────────────────────────────────
    antar_ok = all(len(m["antardasha"]) == 9 for m in result["mahadasha"])
    status = "OK" if antar_ok else "FAIL"
    print(f"  Antar per maha : 9 each  [{status}]")
    if not antar_ok:
        all_pass = False

    # ── 8. Each Antardasha has 9 Pratyantardashas ────────────────────────────
    prat_ok = True
    for m in result["mahadasha"]:
        for a in m["antardasha"]:
            if len(a["pratyantardasha"]) != 9:
                prat_ok = False
                break
    status = "OK" if prat_ok else "FAIL"
    print(f"  Prat per antar : 9 each  [{status}]")
    if not prat_ok:
        all_pass = False

    # ── 9. Current period exists ─────────────────────────────────────────────
    current = result["current_period"]
    cur_ok = "mahadasha" in current and "antardasha" in current
    status = "OK" if cur_ok else "FAIL"
    print(f"  Current period : found  [{status}]")
    if cur_ok:
        cm = current["mahadasha"]
        ca = current["antardasha"]
        cp = current.get("pratyantardasha", {})
        print(f"       Maha      : {cm.get('lord_name', '?')} ({cm.get('start_date', '?')} to {cm.get('end_date', '?')})")
        print(f"       Antar     : {ca.get('lord_name', '?')} ({ca.get('start_date', '?')} to {ca.get('end_date', '?')})")
        if cp:
            print(f"       Pratyantar: {cp.get('lord_name', '?')} ({cp.get('start_date', '?')} to {cp.get('end_date', '?')})")
    else:
        all_pass = False

    # ── 10. Print full Mahadasha timeline ────────────────────────────────────
    print(f"\n  {'Lord':<10} {'Start':<12} {'End':<12} {'Years':>8}")
    print(f"  {'-'*10} {'-'*12} {'-'*12} {'-'*8}")
    for m in result["mahadasha"]:
        print(f"  {m['lord_name']:<10} {m['start_date']:<12} {m['end_date']:<12} {m['duration_years']:>8.4f}")

    # ── Final verdict ────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    if all_pass:
        print("  RESULT : ALL DASHA CHECKS PASSED -- Engine is accurate")
    else:
        print("  RESULT : SOME CHECKS FAILED -- Review above")
    print(f"{'='*60}\n")

    assert all_pass, "Dasha verification failed"


if __name__ == "__main__":
    test_dasha_engine()
