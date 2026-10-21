"""
api/routes/places.py
────────────────────
GET /api/places?q=kochi  →  worldwide place autocomplete suggestions
"""

from fastapi import APIRouter, Query
from app.core.geocoder import search_places_worldwide

router = APIRouter()


@router.get("/places")
async def get_places(q: str = Query(..., min_length=2, description="Place search query")):
    """
    Worldwide place autocomplete suggestions with latitude, longitude, and timezone.
    """
    return search_places_worldwide(q)
