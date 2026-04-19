"""
core/dashas.py
───────────────
Vimshottari Dasha engine.
Computes full Maha → Antar → Pratyantar → Sookshma → Prana tree with exact dates.

Rules:
  - Total cycle = 120 years
  - Moon's birth nakshatra determines starting Mahadasha lord
  - Balance = remaining portion of first Mahadasha based on Moon's
    position within the nakshatra
  - Sub-period sequence always starts with the period lord
  - Duration is proportionally divided: (lord_years / 120) * parent_duration
  - This pattern repeats identically at every level
"""

from datetime import datetime, timedelta
import pytz
from app.core.calculator import calculate_chart, NAKSHATRA_NAMES
from app.core.geocoder import resolve_place

# ── Vimshottari constants ─────────────────────────────────────────────────────

DASHA_SEQUENCE = ["Ke", "Ve", "Su", "Mo", "Ma", "Ra", "Ju", "Sa", "Me"]

DASHA_YEARS = {
    "Ke": 7, "Ve": 20, "Su": 6, "Mo": 10, "Ma": 7,
    "Ra": 18, "Ju": 16, "Sa": 19, "Me": 17,
}  # Total = 120 years

TOTAL_YEARS = 120

DASHA_LORD_NAMES = {
    "Su": "Surya",  "Mo": "Chandra", "Ma": "Mangala", "Me": "Budha",
    "Ju": "Guru",   "Ve": "Shukra",  "Sa": "Shani",
    "Ra": "Rahu",   "Ke": "Ketu",
}

# Nakshatra → lord mapping: index % 9 into DASHA_SEQUENCE
# Ashwini(0)=Ke, Bharani(1)=Ve, Krittika(2)=Su, Rohini(3)=Mo, ...


# ── Helpers ───────────────────────────────────────────────────────────────────

def _years_to_days(years: float) -> float:
    """Convert years to days using standard Vimshottari year = 365.25 days."""
    return years * 365.25


def _add_years(dt: datetime, years: float) -> datetime:
    """Add fractional years to a datetime."""
    return dt + timedelta(days=_years_to_days(years))


def _fmt(dt: datetime) -> str:
    """Format datetime as ISO date string."""
    return dt.strftime("%Y-%m-%d")


def _moon_dasha_balance(moon_lon: float) -> tuple[str, float]:
    """
    Given Moon's sidereal longitude, return:
      - starting Mahadasha lord
      - remaining years in that Mahadasha at birth

    The Moon's nakshatra determines the lord.
    How far through the nakshatra the Moon has progressed tells us
    how much of that Mahadasha has already elapsed.
    """
    nak_span = 360.0 / 27  # 13.333...°
    nak_index = min(int(moon_lon / nak_span), 26)
    lord = DASHA_SEQUENCE[nak_index % 9]
    total = DASHA_YEARS[lord]

    # Fraction of nakshatra already traversed
    elapsed_in_nak = moon_lon % nak_span
    fraction_elapsed = elapsed_in_nak / nak_span  # 0.0 – 1.0

    remaining_years = total * (1.0 - fraction_elapsed)
    return lord, remaining_years


def _rotated_sequence(start_lord: str) -> list[str]:
    """Return DASHA_SEQUENCE rotated to start with the given lord."""
    idx = DASHA_SEQUENCE.index(start_lord)
    return [DASHA_SEQUENCE[(idx + i) % 9] for i in range(9)]


def _sub_duration(lord: str, parent_duration: float) -> float:
    """Duration of a sub-period: (lord_years / 120) * parent_duration."""
    return (DASHA_YEARS[lord] / TOTAL_YEARS) * parent_duration


# ── Tree builders ─────────────────────────────────────────────────────────────

def _build_prana(sookshma_lord: str, sookshma_duration: float,
                 sookshma_start: datetime) -> list[dict]:
    """Build Pranadasha periods (level 5) within one Sookshmadasha."""
    periods = []
    current = sookshma_start
    sequence = _rotated_sequence(sookshma_lord)

    for lord in sequence:
        duration = _sub_duration(lord, sookshma_duration)
        end = _add_years(current, duration)
        periods.append({
            "lord": lord,
            "lord_name": DASHA_LORD_NAMES[lord],
            "start_date": _fmt(current),
            "end_date": _fmt(end),
            "duration_years": round(duration, 8),
        })
        current = end
    return periods


def _build_sookshma(pratyantar_lord: str, pratyantar_duration: float,
                    pratyantar_start: datetime) -> list[dict]:
    """Build Sookshmadasha periods (level 4) within one Pratyantardasha."""
    periods = []
    current = pratyantar_start
    sequence = _rotated_sequence(pratyantar_lord)

    for lord in sequence:
        duration = _sub_duration(lord, pratyantar_duration)
        end = _add_years(current, duration)
        pranas = _build_prana(lord, duration, current)
        periods.append({
            "lord": lord,
            "lord_name": DASHA_LORD_NAMES[lord],
            "start_date": _fmt(current),
            "end_date": _fmt(end),
            "duration_years": round(duration, 8),
            "pranadasha": pranas,
        })
        current = end
    return periods


def _build_pratyantar(antar_lord: str, antar_duration: float,
                      antar_start: datetime) -> list[dict]:
    """Build Pratyantardasha periods (level 3) within one Antardasha."""
    periods = []
    current = antar_start
    sequence = _rotated_sequence(antar_lord)

    for lord in sequence:
        duration = _sub_duration(lord, antar_duration)
        end = _add_years(current, duration)
        sookshmas = _build_sookshma(lord, duration, current)
        periods.append({
            "lord": lord,
            "lord_name": DASHA_LORD_NAMES[lord],
            "start_date": _fmt(current),
            "end_date": _fmt(end),
            "duration_years": round(duration, 6),
            "sookshmadasha": sookshmas,
        })
        current = end
    return periods


def _build_antar(maha_lord: str, maha_duration: float,
                 maha_start: datetime) -> list[dict]:
    """Build Antardasha periods (level 2) within one Mahadasha."""
    periods = []
    current = maha_start
    sequence = _rotated_sequence(maha_lord)

    for lord in sequence:
        duration = _sub_duration(lord, maha_duration)
        end = _add_years(current, duration)
        pratyantars = _build_pratyantar(lord, duration, current)
        periods.append({
            "lord": lord,
            "lord_name": DASHA_LORD_NAMES[lord],
            "start_date": _fmt(current),
            "end_date": _fmt(end),
            "duration_years": round(duration, 6),
            "pratyantardasha": pratyantars,
        })
        current = end
    return periods


def _build_mahadasha(birth_dt: datetime, start_lord: str,
                     balance_years: float) -> list[dict]:
    """Build the full Mahadasha tree (9 periods spanning ~120 years)."""
    periods = []
    current = birth_dt
    sequence = _rotated_sequence(start_lord)

    for i, lord in enumerate(sequence):
        # First period uses the balance (partial), rest use full years
        duration = balance_years if i == 0 else float(DASHA_YEARS[lord])
        end = _add_years(current, duration)
        antardashas = _build_antar(lord, duration, current)
        periods.append({
            "lord": lord,
            "lord_name": DASHA_LORD_NAMES[lord],
            "start_date": _fmt(current),
            "end_date": _fmt(end),
            "duration_years": round(duration, 6),
            "antardasha": antardashas,
        })
        current = end

    return periods


def _find_current(dashas: list[dict], today: str) -> dict:
    """Walk the tree and find active Maha → Antar → Pratyantar → Sookshma → Prana."""
    current = {}
    for maha in dashas:
        if maha["start_date"] <= today <= maha["end_date"]:
            current["mahadasha"] = {
                k: v for k, v in maha.items() if k != "antardasha"
            }
            for antar in maha["antardasha"]:
                if antar["start_date"] <= today <= antar["end_date"]:
                    current["antardasha"] = {
                        k: v for k, v in antar.items()
                        if k != "pratyantardasha"
                    }
                    for prat in antar["pratyantardasha"]:
                        if prat["start_date"] <= today <= prat["end_date"]:
                            current["pratyantardasha"] = {
                                k: v for k, v in prat.items()
                                if k != "sookshmadasha"
                            }
                            for sookshma in prat["sookshmadasha"]:
                                if sookshma["start_date"] <= today <= sookshma["end_date"]:
                                    current["sookshmadasha"] = {
                                        k: v for k, v in sookshma.items()
                                        if k != "pranadasha"
                                    }
                                    for prana in sookshma["pranadasha"]:
                                        if prana["start_date"] <= today <= prana["end_date"]:
                                            current["pranadasha"] = prana
                                            break
                                    break
                            break
                    break
            break
    return current


# ── Public API ────────────────────────────────────────────────────────────────

def calculate_dasha(dob: str, tob: str, place: str) -> dict:
    """
    Compute full Vimshottari Dasha tree + identify current active period.

    Parameters
    ----------
    dob   : "YYYY-MM-DD"
    tob   : "HH:MM"
    place : human-readable birth place

    Returns
    -------
    dict matching DashaResponse schema
    """
    # Get the D1 chart (reuses cached geocoding)
    chart = calculate_chart(dob, tob, place)

    # Moon's sidereal longitude seeds the Dasha
    moon = next(p for p in chart["planets"] if p["id"] == "Mo")
    moon_lon = moon["absolute_lon"]
    moon_nak = moon["nakshatra"]
    moon_pada = moon["pada"]

    start_lord, balance_years = _moon_dasha_balance(moon_lon)

    # Birth datetime (local) as Dasha anchor
    _, _, tz_name = resolve_place(place)
    local_tz = pytz.timezone(tz_name)
    birth_dt = local_tz.localize(
        datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    )

    # Build the full tree
    dashas = _build_mahadasha(birth_dt, start_lord, balance_years)

    # Find what's active today
    today = datetime.now().strftime("%Y-%m-%d")
    current_period = _find_current(dashas, today)

    return {
        "moon_nakshatra": moon_nak,
        "moon_pada": moon_pada,
        "starting_lord": start_lord,
        "starting_lord_name": DASHA_LORD_NAMES[start_lord],
        "balance_at_birth_years": round(balance_years, 4),
        "mahadasha": dashas,
        "current_period": current_period,
    }
