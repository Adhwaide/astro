"""
core/report.py
───────────────
Structured life report generator.

Produces a JSON report with sections: health, career, relationships,
spirituality, current_period_summary. Each section has a summary string
and key_factors array based on classical Vedic rules.
"""

from app.core.calculator import SIGN_NAMES, PLANET_NAMES


# ── Sign classification helpers ───────────────────────────────────────────────

SIGN_ELEMENTS = {
    0: "Fire", 1: "Earth", 2: "Air", 3: "Water",
    4: "Fire", 5: "Earth", 6: "Air", 7: "Water",
    8: "Fire", 9: "Earth", 10: "Air", 11: "Water",
}

# Sign ownership: sign_index → planet_id
SIGN_LORDS = {
    0: "Ma", 1: "Ve", 2: "Me", 3: "Mo",
    4: "Su", 5: "Me", 6: "Ve", 7: "Ma",
    8: "Ju", 9: "Sa", 10: "Sa", 11: "Ju",
}

# Exaltation signs
EXALTATION = {"Su": 0, "Mo": 1, "Ma": 9, "Me": 5, "Ju": 3, "Ve": 11, "Sa": 6}

# Debilitation signs
DEBILITATION = {"Su": 6, "Mo": 7, "Ma": 3, "Me": 11, "Ju": 9, "Ve": 5, "Sa": 0}

# Natural benefics and malefics
BENEFICS = {"Ju", "Ve", "Mo", "Me"}
MALEFICS = {"Su", "Ma", "Sa", "Ra", "Ke"}


def _planet_by_id(planets: list, pid: str) -> dict | None:
    """Find planet dict by id."""
    return next((p for p in planets if p["id"] == pid), None)


def _get_house_lord(house_num: int, houses: list) -> str:
    """Get the lord (planet id) of a given house number (1-12)."""
    sign = houses[house_num - 1]["sign"]
    return SIGN_LORDS[sign]


def _planets_in_house(planets: list, house_num: int) -> list:
    """Return all planets occupying a specific house."""
    return [p for p in planets if p["house"] == house_num]


def _planet_dignity(pid: str, sign: int) -> str:
    """Check dignity: exalted, debilitated, own sign, or neutral."""
    if pid in ("Ra", "Ke"):
        return "neutral"
    if EXALTATION.get(pid) == sign:
        return "exalted"
    if DEBILITATION.get(pid) == sign:
        return "debilitated"
    if SIGN_LORDS.get(sign) == pid:
        return "own_sign"
    return "neutral"


def _describe_dignity(pid: str, sign: int) -> str:
    """Human-readable dignity description."""
    name = PLANET_NAMES.get(pid, pid)
    sign_name = SIGN_NAMES[sign]
    d = _planet_dignity(pid, sign)
    if d == "exalted":
        return f"{name} is exalted in {sign_name} — at maximum strength"
    elif d == "debilitated":
        return f"{name} is debilitated in {sign_name} — weakened condition"
    elif d == "own_sign":
        return f"{name} is in own sign {sign_name} — strong and comfortable"
    else:
        return f"{name} is placed in {sign_name}"


# ── Section generators ────────────────────────────────────────────────────────

def _health_section(planets: list, houses: list, lagna: dict) -> dict:
    """
    Health analysis based on:
    - Lagna lord condition (vitality)
    - 6th house (disease, enemies)
    - 8th house (chronic illness, longevity)
    - Malefics in 1st/6th/8th
    """
    lagna_lord_id = _get_house_lord(1, houses)
    lagna_lord = _planet_by_id(planets, lagna_lord_id)
    factors = []

    if lagna_lord:
        factors.append(_describe_dignity(lagna_lord_id, lagna_lord["sign"]))
        if lagna_lord["house"] in [6, 8, 12]:
            factors.append(f"Lagna lord in {lagna_lord['house']}th house — health needs attention")
        elif lagna_lord["house"] in [1, 4, 7, 10]:
            factors.append(f"Lagna lord in kendra (house {lagna_lord['house']}) — strong constitution")

    # 6th house analysis
    h6_lord_id = _get_house_lord(6, houses)
    h6_planets = _planets_in_house(planets, 6)
    if h6_planets:
        names = ", ".join(p["name"] for p in h6_planets)
        factors.append(f"6th house occupied by {names} — watch for health vulnerabilities")
    h6_lord = _planet_by_id(planets, h6_lord_id)
    if h6_lord and h6_lord["house"] in [1, 2]:
        factors.append(f"6th lord ({h6_lord['name']}) in house {h6_lord['house']} — potential health challenges")

    # 8th house analysis
    h8_planets = _planets_in_house(planets, 8)
    if h8_planets:
        malefic_in_8 = [p["name"] for p in h8_planets if p["id"] in MALEFICS]
        if malefic_in_8:
            factors.append(f"Malefics in 8th house ({', '.join(malefic_in_8)}) — need caution with chronic conditions")

    # Malefics afflicting 1st house
    h1_malefics = [p["name"] for p in _planets_in_house(planets, 1) if p["id"] in MALEFICS]
    if h1_malefics:
        factors.append(f"Malefics in Lagna ({', '.join(h1_malefics)}) — prone to health fluctuations")

    dignity = _planet_dignity(lagna_lord_id, lagna_lord["sign"]) if lagna_lord else "neutral"
    if dignity in ("exalted", "own_sign"):
        summary = "Strong overall vitality indicated. The lagna lord is well-placed, suggesting good physical resilience and recovery capacity."
    elif dignity == "debilitated":
        summary = "Health requires careful attention. The debilitated lagna lord suggests susceptibility to ailments. Regular wellness routines are advised."
    else:
        summary = "Moderate health indications. The constitution is average — maintaining a disciplined lifestyle will support long-term well-being."

    return {"summary": summary, "key_factors": factors}


def _career_section(planets: list, houses: list) -> dict:
    """
    Career analysis based on:
    - 10th house lord condition
    - Planets in 10th house
    - 10th lord's sign element
    """
    h10_lord_id = _get_house_lord(10, houses)
    h10_lord = _planet_by_id(planets, h10_lord_id)
    factors = []

    if h10_lord:
        factors.append(_describe_dignity(h10_lord_id, h10_lord["sign"]))
        factors.append(f"10th lord ({h10_lord['name']}) placed in house {h10_lord['house']}")

    h10_planets = _planets_in_house(planets, 10)
    if h10_planets:
        names = ", ".join(p["name"] for p in h10_planets)
        factors.append(f"10th house occupied by {names}")

        # Career indications by planet
        for p in h10_planets:
            if p["id"] == "Su":
                factors.append("Sun in 10th — leadership roles, government, authority positions")
            elif p["id"] == "Mo":
                factors.append("Moon in 10th — public-facing career, hospitality, healthcare")
            elif p["id"] == "Ma":
                factors.append("Mars in 10th — engineering, military, sports, surgery")
            elif p["id"] == "Me":
                factors.append("Mercury in 10th — business, communication, IT, writing")
            elif p["id"] == "Ju":
                factors.append("Jupiter in 10th — teaching, law, advisory, finance")
            elif p["id"] == "Ve":
                factors.append("Venus in 10th — arts, entertainment, luxury industries")
            elif p["id"] == "Sa":
                factors.append("Saturn in 10th — hard-won success, discipline-based career, manufacturing")
    else:
        factors.append("No planets in 10th house — career defined primarily by 10th lord's placement")

    # 10th house sign element for career flavor
    h10_sign = houses[9]["sign"]
    element = SIGN_ELEMENTS[h10_sign]
    element_desc = {
        "Fire": "dynamic, entrepreneurial energy in career",
        "Earth": "practical, results-oriented career approach",
        "Air": "intellectual, communication-driven career path",
        "Water": "intuitive, service-oriented or creative career"
    }
    factors.append(f"10th house in {SIGN_NAMES[h10_sign]} ({element}) — {element_desc[element]}")

    dignity = _planet_dignity(h10_lord_id, h10_lord["sign"]) if h10_lord else "neutral"
    if dignity in ("exalted", "own_sign"):
        summary = "Excellent career prospects. The 10th lord is powerfully placed, indicating professional success, recognition, and steady career growth."
    elif dignity == "debilitated":
        summary = "Career path may face obstacles and delays. Perseverance and skill development are key. Consider alternative or unconventional career paths."
    else:
        summary = "Steady career development is indicated. Success will come through consistent effort and leveraging natural talents."

    return {"summary": summary, "key_factors": factors}


def _relationships_section(planets: list, houses: list) -> dict:
    """
    Relationships based on:
    - 7th house lord
    - Venus condition
    - Planets in 7th house
    """
    h7_lord_id = _get_house_lord(7, houses)
    h7_lord = _planet_by_id(planets, h7_lord_id)
    venus = _planet_by_id(planets, "Ve")
    factors = []

    if h7_lord:
        factors.append(_describe_dignity(h7_lord_id, h7_lord["sign"]))
        factors.append(f"7th lord ({h7_lord['name']}) in house {h7_lord['house']}")
        if h7_lord["house"] in [6, 8, 12]:
            factors.append(f"7th lord in dusthana (house {h7_lord['house']}) — relationship challenges possible")

    if venus:
        factors.append(_describe_dignity("Ve", venus["sign"]))
        if venus["retrograde"]:
            factors.append("Venus retrograde — unconventional approach to love and relationships")

    h7_planets = _planets_in_house(planets, 7)
    if h7_planets:
        names = ", ".join(p["name"] for p in h7_planets)
        factors.append(f"7th house occupied by {names}")
        malefic_in_7 = [p["name"] for p in h7_planets if p["id"] in MALEFICS]
        if malefic_in_7:
            factors.append(f"Malefics in 7th ({', '.join(malefic_in_7)}) — need patience in partnerships")

    venus_dignity = _planet_dignity("Ve", venus["sign"]) if venus else "neutral"
    h7_dignity = _planet_dignity(h7_lord_id, h7_lord["sign"]) if h7_lord else "neutral"

    if venus_dignity in ("exalted", "own_sign") or h7_dignity in ("exalted", "own_sign"):
        summary = "Favorable relationship prospects. Strong indications of a harmonious partnership, emotional fulfillment, and deep bonding."
    elif venus_dignity == "debilitated" or h7_dignity == "debilitated":
        summary = "Relationships may require extra effort and understanding. Delays or unconventional partnerships are possible. Self-work enhances relationship quality."
    else:
        summary = "Moderate relationship indications. A balanced approach to partnerships with both joyful and learning experiences."

    return {"summary": summary, "key_factors": factors}


def _spirituality_section(planets: list, houses: list) -> dict:
    """
    Spirituality based on:
    - 12th house lord
    - Jupiter condition
    - Ketu placement
    - 9th house (dharma)
    """
    h12_lord_id = _get_house_lord(12, houses)
    h12_lord = _planet_by_id(planets, h12_lord_id)
    jupiter = _planet_by_id(planets, "Ju")
    ketu = _planet_by_id(planets, "Ke")
    factors = []

    if h12_lord:
        factors.append(_describe_dignity(h12_lord_id, h12_lord["sign"]))
        factors.append(f"12th lord ({h12_lord['name']}) in house {h12_lord['house']}")

    if jupiter:
        factors.append(_describe_dignity("Ju", jupiter["sign"]))
        factors.append(f"Jupiter in house {jupiter['house']} in {jupiter['sign_name']}")

    if ketu:
        factors.append(f"Ketu (moksha karaka) in house {ketu['house']} in {ketu['sign_name']}")
        if ketu["house"] in [1, 5, 9, 12]:
            factors.append("Ketu in a spiritual house — strong inclination toward inner life and liberation")

    # 9th house (dharma)
    h9_lord_id = _get_house_lord(9, houses)
    h9_lord = _planet_by_id(planets, h9_lord_id)
    h9_planets = _planets_in_house(planets, 9)
    if h9_lord:
        factors.append(f"9th lord (dharma) is {h9_lord['name']} in house {h9_lord['house']}")
    if h9_planets:
        names = ", ".join(p["name"] for p in h9_planets)
        factors.append(f"Planets in 9th house: {names} — strong dharmic tendencies")

    ju_dignity = _planet_dignity("Ju", jupiter["sign"]) if jupiter else "neutral"
    if ju_dignity in ("exalted", "own_sign"):
        summary = "Deep spiritual potential. Jupiter's strength indicates wisdom, philosophical depth, and natural attraction to higher knowledge and truth."
    elif ketu and ketu["house"] in [1, 9, 12]:
        summary = "Moksha-oriented chart. Ketu's placement indicates past-life spiritual evolution continuing in this life, leading toward detachment and liberation."
    else:
        summary = "Spiritual growth is available through conscious effort. Practices like meditation, study of sacred texts, and service will deepen inner realization."

    return {"summary": summary, "key_factors": factors}


def _current_period_section(planets: list, houses: list, current_period: dict) -> dict:
    """
    Current period summary based on:
    - Current Mahadasha lord's placement
    - Its relationship with Lagna lord
    """
    factors = []

    maha_info = current_period.get("mahadasha", {})
    antar_info = current_period.get("antardasha", {})
    maha_lord_id = maha_info.get("lord")
    antar_lord_id = antar_info.get("lord")

    if maha_lord_id:
        maha_planet = _planet_by_id(planets, maha_lord_id)
        if maha_planet:
            factors.append(f"Current Mahadasha: {maha_planet['name']} ({maha_info.get('start_date', '?')} to {maha_info.get('end_date', '?')})")
            factors.append(_describe_dignity(maha_lord_id, maha_planet["sign"]))
            factors.append(f"Mahadasha lord in house {maha_planet['house']} — this house's themes dominate this period")

            # Benefic or malefic nature
            nature = "benefic" if maha_lord_id in BENEFICS else "malefic"
            factors.append(f"Mahadasha lord is naturally {nature}")

    if antar_lord_id:
        antar_planet = _planet_by_id(planets, antar_lord_id)
        if antar_planet:
            factors.append(f"Current Antardasha: {antar_planet['name']} in house {antar_planet['house']}")

    # Lagna lord relationship
    lagna_lord_id = _get_house_lord(1, houses)
    if maha_lord_id and lagna_lord_id:
        maha_p = _planet_by_id(planets, maha_lord_id)
        lagna_p = _planet_by_id(planets, lagna_lord_id)
        if maha_p and lagna_p:
            house_diff = abs(maha_p["house"] - lagna_p["house"])
            if house_diff in [0, 3, 6, 9]:
                factors.append(f"Mahadasha lord in kendra from Lagna lord — supportive period for personal growth")
            elif house_diff in [4, 8]:
                factors.append(f"Mahadasha lord in trikona from Lagna lord — auspicious period ahead")

    maha_dignity = "neutral"
    if maha_lord_id:
        mp = _planet_by_id(planets, maha_lord_id)
        if mp:
            maha_dignity = _planet_dignity(maha_lord_id, mp["sign"])

    if maha_dignity in ("exalted", "own_sign"):
        summary = "An empowering current period. The Mahadasha lord is strong, bringing positive developments aligned with its house themes."
    elif maha_dignity == "debilitated":
        summary = "A period requiring patience and resilience. The debilitated Mahadasha lord may bring challenges that ultimately serve as growth catalysts."
    else:
        summary = "A period of steady progress. Results will manifest proportionally to effort invested. Stay focused on long-term objectives."

    return {"summary": summary, "key_factors": factors}


# ── Public API ────────────────────────────────────────────────────────────────

def generate_life_report(chart: dict, dasha_data: dict) -> dict:
    """
    Generate a structured life report.

    Parameters
    ----------
    chart      : D1 chart data from calculate_chart()
    dasha_data : Dasha data from calculate_dasha()

    Returns
    -------
    dict matching LifeReportResponse schema
    """
    planets = chart["planets"]
    houses = chart["houses"]
    lagna = chart["lagna"]
    current_period = dasha_data.get("current_period", {})

    return {
        "health": _health_section(planets, houses, lagna),
        "career": _career_section(planets, houses),
        "relationships": _relationships_section(planets, houses),
        "spirituality": _spirituality_section(planets, houses),
        "current_period_summary": _current_period_section(planets, houses, current_period),
    }
