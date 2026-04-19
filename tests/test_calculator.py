"""
tests/test_calculator.py
─────────────────────────
Verifies calculator output against a known, manually verified chart.

Test chart: Kochi, Kerala — 2004-02-28 — 01:15 IST
Expected placements (Lahiri ayanamsha):
  Lagna  : Vrischika (Scorpio)   — sign index 7
  Surya  : Kumbha (Aquarius)     — house 4
  Chandra: Vrishabha (Taurus)    — house 7
  Mangala: Mesha (Aries)         — house 6  (conjunct Rahu)
  Budha  : Kumbha (Aquarius)     — house 4
  Guru   : Karka (Cancer)  OR    — verify against Jagannatha Hora
  Shukra : Meena (Pisces)        — house 5  (exalted)
  Shani  : Mithuna (Gemini)      — house 8  (retrograde)
  Rahu   : Mesha (Aries)         — house 6
  Ketu   : Tula (Libra)          — house 12

Run with:
    cd backend
    python -m pytest tests/test_calculator.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.calculator import calculate_chart

# ── Known birth data ──────────────────────────────────────────────────────────
DOB   = "2004-02-28"
TOB   = "01:15"
PLACE = "Kochi, Kerala, India"

# ── Expected values (from Jagannatha Hora / manual verification) ──────────────
EXPECTED_LAGNA_SIGN = 7          # Vrischika

EXPECTED_PLANETS = {
    "Su": {"sign": 10, "house": 4,  "retrograde": False},   # Kumbha
    "Mo": {"sign": 1,  "house": 7,  "retrograde": False},   # Vrishabha
    "Ma": {"sign": 0,  "house": 6,  "retrograde": False},   # Mesha
    "Me": {"sign": 10, "house": 4,  "retrograde": False},   # Kumbha
    "Ve": {"sign": 11, "house": 5,  "retrograde": False},   # Meena (exalted)
    "Sa": {"sign": 2,  "house": 8,  "retrograde": True},    # Mithuna (retro)
    "Ra": {"sign": 0,  "house": 6,  "retrograde": True},    # Mesha
    "Ke": {"sign": 6,  "house": 12, "retrograde": True},    # Tula
}

SIGN_NAMES = [
    "Mesha","Vrishabha","Mithuna","Karka",
    "Simha","Kanya","Tula","Vrischika",
    "Dhanu","Makara","Kumbha","Meena",
]


def test_full_chart():
    print(f"\n{'='*60}")
    print(f"  JYOTISHA ENGINE — VERIFICATION TEST")
    print(f"  Birth: {DOB} {TOB} IST | {PLACE}")
    print(f"{'='*60}\n")

    result = calculate_chart(DOB, TOB, PLACE)

    # ── Print meta ────────────────────────────────────────────────────────────
    meta = result["meta"]
    print(f"  Ayanamsha  : {meta['ayanamsha']} ({meta['ayanamsha_value']:.4f}°)")
    print(f"  Location   : {meta['latitude']:.4f}°N, {meta['longitude']:.4f}°E")
    print(f"  Timezone   : {meta['timezone']}")
    print(f"  UTC time   : {meta['utc_time']}")
    print(f"  Julian Day : {meta['julian_day']}\n")

    # ── Check Lagna ───────────────────────────────────────────────────────────
    lagna = result["lagna"]
    lagna_ok = lagna["sign"] == EXPECTED_LAGNA_SIGN
    status = "✓" if lagna_ok else "✗ MISMATCH"
    print(f"  LAGNA : {lagna['sign_name']} {lagna['degree']:.2f}°  {status}")
    if not lagna_ok:
        print(f"          Expected: {SIGN_NAMES[EXPECTED_LAGNA_SIGN]}")

    print()

    # ── Check planets ─────────────────────────────────────────────────────────
    all_pass = lagna_ok
    planet_map = {p["id"]: p for p in result["planets"]}

    print(f"  {'ID':<4} {'Name':<10} {'Sign':<14} {'Deg':>6}  {'Nak':<22} {'H':>2}  {'R':<3}  {'Status'}")
    print(f"  {'-'*4} {'-'*10} {'-'*14} {'-'*6}  {'-'*22} {'-'*2}  {'-'*3}  {'-'*10}")

    for pid, expected in EXPECTED_PLANETS.items():
        p = planet_map.get(pid)
        if p is None:
            print(f"  {pid:<4} NOT FOUND IN OUTPUT")
            all_pass = False
            continue

        sign_ok  = p["sign"]      == expected["sign"]
        house_ok = p["house"]     == expected["house"]
        retro_ok = p["retrograde"] == expected["retrograde"]
        ok = sign_ok and house_ok and retro_ok
        if not ok:
            all_pass = False

        retro_str = "℞" if p["retrograde"] else " "
        status    = "✓" if ok else "✗"

        print(f"  {p['id']:<4} {p['name']:<10} {p['sign_name']:<14} {p['degree']:>6.2f}°"
              f"  {p['nakshatra']:<22} {p['house']:>2}  {retro_str:<3}  {status}")

        if not sign_ok:
            print(f"       ^ Sign expected  : {SIGN_NAMES[expected['sign']]}")
        if not house_ok:
            print(f"       ^ House expected : {expected['house']}")

    # ── Also print Ju (not in strict expected but useful to see) ─────────────
    ju = planet_map.get("Ju")
    if ju:
        print(f"\n  {'Ju':<4} {ju['name']:<10} {ju['sign_name']:<14} {ju['degree']:>6.2f}°"
              f"  {ju['nakshatra']:<22} {ju['house']:>2}  {'℞' if ju['retrograde'] else ' ':<3}  (verify manually)")

    # ── Final verdict ─────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    if all_pass:
        print("  RESULT : ALL CHECKS PASSED ✓ — Engine is accurate")
    else:
        print("  RESULT : SOME CHECKS FAILED ✗ — Review mismatches above")
        print("  Tip    : Cross-check with Jagannatha Hora or Astro-Seek")
    print(f"{'='*60}\n")

    assert all_pass, "Chart verification failed — see output above"


if __name__ == "__main__":
    test_full_chart()