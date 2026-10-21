"""
core/geocoder.py
─────────────────
Place → (latitude, longitude, timezone) resolution with multi-tiered fallback:
1. In-memory LRU cache
2. Open-Meteo Geocoding API (fast, worldwide, free, includes timezones, no 429 rate limits)
3. Photon (Komoot / OSM) API
4. Nominatim with timeout & error handling
5. Local TimezoneFinder for accurate IANA tz resolution
"""

import threading
from functools import lru_cache
from typing import Optional
import httpx
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder

# ── Singletons ───────────────────────────────────────────────────────────────
_geolocator = Nominatim(user_agent="jyotisha_astro_engine_prod_v2", timeout=6)
_tz_finder = TimezoneFinder()
_geo_lock = threading.Lock()


def _query_open_meteo(place: str) -> Optional[tuple[float, float, str]]:
    """Query Open-Meteo Geocoding API with smart token matching."""
    try:
        tokens = [t.strip() for t in place.split(",") if t.strip()]
        city_candidate = tokens[0] if tokens else place
        params = {
            "name": city_candidate,
            "count": 10,
            "language": "en",
            "format": "json"
        }
        with httpx.Client(timeout=5.0) as client:
            r = client.get("https://geocoding-api.open-meteo.com/v1/search", params=params)
            if r.status_code != 200:
                return None
            results = r.json().get("results", [])

            # If no results and full query was different, try full string
            if not results and city_candidate != place:
                r2 = client.get(
                    "https://geocoding-api.open-meteo.com/v1/search",
                    params={"name": place, "count": 10, "language": "en", "format": "json"}
                )
                if r2.status_code == 200:
                    results = r2.json().get("results", [])

            if not results:
                return None

            # Score by extra tokens (state, country) if present
            if len(tokens) > 1 and len(results) > 1:
                other_tokens = [t.lower() for t in tokens[1:]]

                def score(item):
                    s = 0
                    country = (item.get("country") or "").lower()
                    admin1 = (item.get("admin1") or "").lower()
                    admin2 = (item.get("admin2") or "").lower()
                    for ot in other_tokens:
                        if ot in country:
                            s += 3
                        if ot in admin1:
                            s += 3
                        if ot in admin2:
                            s += 2
                    return s

                results.sort(key=score, reverse=True)

            best = results[0]
            lat = float(best["latitude"])
            lon = float(best["longitude"])
            tz = best.get("timezone") or _tz_finder.timezone_at(lat=lat, lng=lon)
            if tz:
                return lat, lon, tz
    except Exception:
        pass
    return None


def _query_photon(place: str) -> Optional[tuple[float, float, str]]:
    """Query Photon (Komoot OSM) as secondary fallback."""
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get(
                "https://photon.komoot.io/api/",
                params={"q": place, "limit": 1},
                headers={"User-Agent": "JyotishaAstro/2.0"}
            )
            if r.status_code == 200:
                features = r.json().get("features", [])
                if features:
                    coords = features[0]["geometry"]["coordinates"]
                    lon, lat = float(coords[0]), float(coords[1])
                    tz = _tz_finder.timezone_at(lat=lat, lng=lon)
                    if tz:
                        return lat, lon, tz
    except Exception:
        pass
    return None


def _query_nominatim(place: str) -> Optional[tuple[float, float, str]]:
    """Query Nominatim with exception silencing."""
    try:
        location = _geolocator.geocode(place)
        if location:
            lat, lon = location.latitude, location.longitude
            tz = _tz_finder.timezone_at(lat=lat, lng=lon)
            if tz:
                return lat, lon, tz
    except (GeocoderTimedOut, GeocoderServiceError):
        pass
    except Exception:
        pass
    return None


@lru_cache(maxsize=512)
def resolve_place(place: str) -> tuple[float, float, str]:
    """
    Resolve a human-readable place string to (lat, lon, timezone).
    Multi-tiered fallback with thread synchronization to prevent duplicate spikes.
    """
    clean_place = place.strip()
    if not clean_place:
        raise ValueError("Place cannot be empty")

    with _geo_lock:
        # Tier 1: Open-Meteo
        res = _query_open_meteo(clean_place)
        if res:
            return res

        # Tier 2: Photon
        res = _query_photon(clean_place)
        if res:
            return res

        # Tier 3: Nominatim
        res = _query_nominatim(clean_place)
        if res:
            return res

    raise ValueError(f"Place not found: '{place}'. Please select a location from the search suggestions.")


def search_places_worldwide(query: str, limit: int = 10) -> list[dict]:
    """
    Search places worldwide for autocomplete suggestions.
    Returns list of dicts with name, state, country, lat, lon, timezone, displayName.
    """
    clean_query = query.strip()
    if not clean_query or len(clean_query) < 2:
        return []

    try:
        params = {
            "name": clean_query,
            "count": min(max(limit, 1), 20),
            "language": "en",
            "format": "json"
        }
        with httpx.Client(timeout=4.0) as client:
            r = client.get("https://geocoding-api.open-meteo.com/v1/search", params=params)
            if r.status_code == 200:
                results = r.json().get("results", [])
                out = []
                for item in results:
                    name = item.get("name", "")
                    admin1 = item.get("admin1") or ""
                    country = item.get("country") or ""
                    country_code = item.get("country_code") or ""
                    lat = item.get("latitude")
                    lon = item.get("longitude")
                    tz = item.get("timezone") or _tz_finder.timezone_at(lat=lat, lng=lon)

                    # Build clean display string e.g. "Kochi, Kerala, India"
                    parts = [p for p in [name, admin1, country] if p]
                    display_name = ", ".join(parts)

                    out.append({
                        "name": name,
                        "state": admin1,
                        "country": country,
                        "country_code": country_code,
                        "latitude": lat,
                        "longitude": lon,
                        "timezone": tz or "UTC",
                        "display_name": display_name
                    })
                return out
    except Exception:
        pass
    return []
