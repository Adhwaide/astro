"""
core/calculator.py
──────────────────
Swiss Ephemeris wrapper for Vedic (sidereal) chart calculation.
Handles Julian Day conversion and returns clean planet/lagna data
for all 9 grahas.

Ayanamsha : Lahiri (default) — configurable via AYANAMSHA env var
Ephemeris  : looks for .se1 files in ephe/
"""

import os
import swisseph as swe
from datetime import datetime
import pytz
from dotenv import load_dotenv
from app.core.geocoder import resolve_place

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
EPHE_PATH = os.path.join(BASE_DIR, "ephe")
swe.set_ephe_path(EPHE_PATH)

# ── Ayanamsha ────────────────────────────────────────────────────────────────
AYANAMSHA_MAP = {
    "lahiri":     swe.SIDM_LAHIRI,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "raman":      swe.SIDM_RAMAN,
    "yukteshwar": swe.SIDM_YUKTESHWAR,
}
AYANAMSHA_NAME = os.getenv("AYANAMSHA", "lahiri").lower()
swe.set_sid_mode(AYANAMSHA_MAP.get(AYANAMSHA_NAME, swe.SIDM_LAHIRI))

# ── Lookup tables ─────────────────────────────────────────────────────────────
SIGN_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka",
    "Simha", "Kanya", "Tula", "Vrischika",
    "Dhanu", "Makara", "Kumbha", "Meena",
]

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Swiss Ephemeris planet IDs
PLANET_IDS = {
    "Su": swe.SUN,
    "Mo": swe.MOON,
    "Ma": swe.MARS,
    "Me": swe.MERCURY,
    "Ju": swe.JUPITER,
    "Ve": swe.VENUS,
    "Sa": swe.SATURN,
    "Ra": swe.MEAN_NODE,   # Rahu — mean node
}

PLANET_NAMES = {
    "Su": "Surya",
    "Mo": "Chandra",
    "Ma": "Mangala",
    "Me": "Budha",
    "Ju": "Guru",
    "Ve": "Shukra",
    "Sa": "Shani",
    "Ra": "Rahu",
    "Ke": "Ketu",
}


# ── Helpers (public — shared with dashas.py) ─────────────────────────────────

def nakshatra_pada(lon: float) -> tuple[str, int]:
    """
    Return (nakshatra_name, pada) for a sidereal longitude.
    Each nakshatra = 13°20' = 13.333...°
    Each pada = 3°20' = 3.333...°
    """
    nak_index = int(lon / (360 / 27))          # 0–26
    nak_index = min(nak_index, 26)
    position_in_nak = lon % (360 / 27)
    pada = int(position_in_nak / (360 / 108)) + 1   # 1–4
    pada = min(pada, 4)
    return NAKSHATRA_NAMES[nak_index], pada


def normalize(lon: float) -> float:
    """Normalize longitude to 0–360."""
    return lon % 360


def local_to_utc(dob: str, tob: str, tz_name: str) -> datetime:
    """Convert local birth datetime string to UTC datetime."""
    local_tz = pytz.timezone(tz_name)
    naive_dt = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    local_dt = local_tz.localize(naive_dt)
    return local_dt.astimezone(pytz.utc)


def to_julian_day(utc_dt: datetime) -> float:
    """Convert UTC datetime to Julian Day Number."""
    hour_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)


# ── Main function ─────────────────────────────────────────────────────────────

def calculate_chart(dob: str, tob: str, place: str) -> dict:
    """
    Full Vedic chart calculation.

    Parameters
    ----------
    dob   : "YYYY-MM-DD"
    tob   : "HH:MM"
    place : human-readable birth place

    Returns
    -------
    dict matching ChartResponse schema in models/request.py
    """

    # 1. Geocode + Timezone (cached)
    lat, lon, tz_name = resolve_place(place)

    # 2. UTC conversion
    utc_dt = local_to_utc(dob, tob, tz_name)

    # 3. Julian Day
    jd = to_julian_day(utc_dt)

    # 4. Ayanamsha value at this JD
    ayanamsha_val = swe.get_ayanamsa_ut(jd)

    # 5. Compute Ascendant
    #    swe.houses returns (cusps, ascmc) — ascmc[0] is tropical ASC
    cusps, ascmc = swe.houses(jd, lat, lon, b"P")   # Placidus (ASC same for all)
    tropical_asc = ascmc[0]
    sidereal_asc = normalize(tropical_asc - ayanamsha_val)
    lagna_sign = int(sidereal_asc / 30)
    lagna_degree = sidereal_asc % 30

    # 6. Compute all planets
    planets_out = []

    for pid, swe_id in PLANET_IDS.items():
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        result, ret_flag = swe.calc_ut(jd, swe_id, flags)
        lon_sid = normalize(result[0])
        speed = result[3]                  # deg/day
        retrograde = speed < 0

        sign = int(lon_sid / 30)
        degree_in_sign = lon_sid % 30
        nakshatra, pada = nakshatra_pada(lon_sid)
        house = ((sign - lagna_sign) % 12) + 1

        planets_out.append({
            "id": pid,
            "name": PLANET_NAMES[pid],
            "sign": sign,
            "sign_name": SIGN_NAMES[sign],
            "degree": round(degree_in_sign, 4),
            "absolute_lon": round(lon_sid, 4),
            "nakshatra": nakshatra,
            "pada": pada,
            "house": house,
            "retrograde": retrograde,
            "speed": round(speed, 6),
        })

    # 7. Ketu = Rahu + 180°
    rahu = next(p for p in planets_out if p["id"] == "Ra")
    ketu_lon = normalize(rahu["absolute_lon"] + 180.0)
    ketu_sign = int(ketu_lon / 30)
    ketu_degree = ketu_lon % 30
    ketu_nak, ketu_pada = nakshatra_pada(ketu_lon)
    ketu_house = ((ketu_sign - lagna_sign) % 12) + 1

    planets_out.append({
        "id": "Ke",
        "name": PLANET_NAMES["Ke"],
        "sign": ketu_sign,
        "sign_name": SIGN_NAMES[ketu_sign],
        "degree": round(ketu_degree, 4),
        "absolute_lon": round(ketu_lon, 4),
        "nakshatra": ketu_nak,
        "pada": ketu_pada,
        "house": ketu_house,
        "retrograde": True,   # Ketu always retrograde by convention
        "speed": round(-rahu["speed"], 6),
    })

    # 8. House sign list (for chart rendering)
    houses_out = []
    for h in range(12):
        sign_index = (lagna_sign + h) % 12
        houses_out.append({
            "house": h + 1,
            "sign": sign_index,
            "sign_name": SIGN_NAMES[sign_index],
        })

    return {
        "lagna": {
            "sign": lagna_sign,
            "sign_name": SIGN_NAMES[lagna_sign],
            "degree": round(lagna_degree, 4),
        },
        "planets": planets_out,
        "houses": houses_out,
        "meta": {
            "ayanamsha": AYANAMSHA_NAME.capitalize(),
            "ayanamsha_value": round(ayanamsha_val, 6),
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "timezone": tz_name,
            "julian_day": round(jd, 6),
            "utc_time": utc_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
        },
    }
