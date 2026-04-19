"""
core/geocoder.py
─────────────────
Place → (latitude, longitude, timezone) resolution with caching.
Uses Nominatim for geocoding and TimezoneFinder for tz resolution.
"""

from functools import lru_cache
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder

# ── Singletons (avoid re-creating on every request) ──────────────────────────
_geolocator = Nominatim(user_agent="jyotisha_engine_v1", timeout=10)
_tz_finder = TimezoneFinder()


@lru_cache(maxsize=256)
def resolve_place(place: str) -> tuple[float, float, str]:
    """
    Resolve a human-readable place string to (lat, lon, timezone).

    Uses LRU cache so repeated calls for the same place are instant.
    """
    try:
        location = _geolocator.geocode(place)
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        raise ValueError(f"Geocoding failed for '{place}': {e}")
    if location is None:
        raise ValueError(f"Place not found: '{place}'. Try adding state/country.")

    lat, lon = location.latitude, location.longitude

    tz = _tz_finder.timezone_at(lat=lat, lng=lon)
    if tz is None:
        raise ValueError(f"Could not determine timezone for lat={lat}, lon={lon}")

    return lat, lon, tz
