"""
core/divisional.py
───────────────────
Vedic divisional chart (Varga) calculator.

Supports: D1 (Rasi), D2 (Hora), D9 (Navamsha), D10 (Dasamsa), D30 (Trimsamsa)

Each function takes a planet's sidereal longitude and its D1 rasi (sign index 0-11),
and returns the divisional sign index (0-11).
"""

from app.core.calculator import (
    calculate_chart,
    SIGN_NAMES,
    PLANET_NAMES,
    nakshatra_pada,
    normalize,
)


# ── Division rules ────────────────────────────────────────────────────────────

def _d2_hora(sign: int, degree: float) -> int:
    """
    D2 — Hora Chart
    Odd signs (Mesha, Mithuna, Simha …):  0–15° → Leo(4), 15–30° → Cancer(3)
    Even signs (Vrishabha, Karka, Kanya …): 0–15° → Cancer(3), 15–30° → Leo(4)
    """
    is_odd = (sign % 2 == 0)  # sign index 0=Mesha (odd), 1=Vrishabha (even)
    if is_odd:
        return 4 if degree < 15.0 else 3   # Leo then Cancer
    else:
        return 3 if degree < 15.0 else 4   # Cancer then Leo


def _d9_navamsha(sign: int, degree: float) -> int:
    """
    D9 — Navamsha Chart
    Each sign is divided into 9 parts of 3°20' (3.3333…°).
    Starting navamsha for each element:
        Fire signs (0,4,8): starts from Mesha (0)
        Earth signs (1,5,9): starts from Makara (9)
        Air signs  (2,6,10): starts from Tula (6)
        Water signs (3,7,11): starts from Karka (3)
    """
    element_starts = {0: 0, 1: 9, 2: 6, 3: 3}
    element = sign % 4
    start = element_starts[element]
    # Add a tiny epsilon to prevent floating-point truncation at exact boundaries
    division = min(int((degree * 9 / 30.0) + 1e-9), 8)  # 0–8
    return (start + division) % 12


def _d10_dasamsa(sign: int, degree: float) -> int:
    """
    D10 — Dasamsa Chart (Parashari method)
    Each sign is divided into 10 parts of 3° each.
    Odd signs: count starts from the same sign.
    Even signs: count starts from the 9th sign from it.
    """
    division = min(int(degree / 3.0), 9)  # 0–9
    is_odd = (sign % 2 == 0)  # index 0=Mesha is odd
    if is_odd:
        return (sign + division) % 12
    else:
        return (sign + 9 + division) % 12


def _d30_trimsamsa(sign: int, degree: float) -> int:
    """
    D30 — Trimsamsa Chart
    Unequal divisions within each sign.
    Odd signs: Mars(5°), Saturn(5°), Jupiter(8°), Mercury(7°), Venus(5°)
    Even signs: Venus(5°), Mercury(7°), Jupiter(8°), Saturn(5°), Mars(5°)

    The lord maps to a specific sign:
        Mars→Mesha(0), Saturn→Kumbha(10), Jupiter→Dhanu(8),
        Mercury→Mithuna(2), Venus→Tula(6)
    """
    is_odd = (sign % 2 == 0)  # index 0=Mesha is odd
    if is_odd:
        # Odd sign: Ma 0-5 (Aries=0), Sa 5-10 (Aquarius=10), Ju 10-18 (Sag=8), Me 18-25 (Gemini=2), Ve 25-30 (Libra=6)
        if degree < 5.0: return 0
        elif degree < 10.0: return 10
        elif degree < 18.0: return 8
        elif degree < 25.0: return 2
        else: return 6
    else:
        # Even sign: Ve 0-5 (Taurus=1), Me 5-12 (Virgo=5), Ju 12-20 (Pisces=11), Sa 20-25 (Capricorn=9), Ma 25-30 (Scorpio=7)
        if degree < 5.0: return 1
        elif degree < 12.0: return 5
        elif degree < 20.0: return 11
        elif degree < 25.0: return 9
        else: return 7


DIVISIONAL_FUNCS = {
    "D2": _d2_hora,
    "D9": _d9_navamsha,
    "D10": _d10_dasamsa,
    "D30": _d30_trimsamsa,
}


# ── Public API ────────────────────────────────────────────────────────────────

def calculate_divisional(dob: str, tob: str, place: str, chart_type: str) -> dict:
    """
    Compute a divisional chart.

    Parameters
    ----------
    dob        : "YYYY-MM-DD"
    tob        : "HH:MM"
    place      : human-readable birth place
    chart_type : "D1", "D2", "D9", "D10", or "D30"

    Returns
    -------
    dict matching ChartResponse schema (same structure as /api/chart)
    """
    # Get the D1 (Rasi) chart first — all divisions are based on D1 longitudes
    d1 = calculate_chart(dob, tob, place)

    if chart_type == "D1":
        return d1

    if chart_type not in DIVISIONAL_FUNCS:
        raise ValueError(f"Unsupported chart type: {chart_type}. Supported: D1, D2, D9, D10, D30")

    div_func = DIVISIONAL_FUNCS[chart_type]

    # Compute the divisional Lagna
    d1_lagna = d1["lagna"]
    lagna_div_sign = div_func(d1_lagna["sign"], d1_lagna["degree"])

    # Recompute each planet's divisional sign
    planets_out = []
    for p in d1["planets"]:
        div_sign = div_func(p["sign"], p["degree"])
        div_degree = p["degree"]  # degree within sign stays the same for display
        div_house = ((div_sign - lagna_div_sign) % 12) + 1
        nak, pada = nakshatra_pada(p["absolute_lon"])

        planets_out.append({
            "id": p["id"],
            "name": p["name"],
            "sign": div_sign,
            "sign_name": SIGN_NAMES[div_sign],
            "degree": round(div_degree, 4),
            "absolute_lon": p["absolute_lon"],
            "nakshatra": nak,
            "pada": pada,
            "house": div_house,
            "retrograde": p["retrograde"],
            "speed": p["speed"],
        })

    # Build house list from divisional lagna
    houses_out = []
    for h in range(12):
        sign_index = (lagna_div_sign + h) % 12
        houses_out.append({
            "house": h + 1,
            "sign": sign_index,
            "sign_name": SIGN_NAMES[sign_index],
        })

    return {
        "chart_type": chart_type,
        "lagna": {
            "sign": lagna_div_sign,
            "sign_name": SIGN_NAMES[lagna_div_sign],
            "degree": round(d1_lagna["degree"], 4),
        },
        "planets": planets_out,
        "houses": houses_out,
        "meta": {
            **d1["meta"],
            "chart_type": chart_type,
        },
    }
