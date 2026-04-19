"""
api/routes/dasha.py
────────────────────
POST /api/dasha  →  full Vimshottari Dasha tree + current period
"""

from fastapi import APIRouter, HTTPException
from app.models.request import BirthData, DashaResponse
from app.core.dashas import calculate_dasha

router = APIRouter()


@router.post("/dasha", response_model=DashaResponse)
async def get_dasha(data: BirthData):
    """
    Generate Vimshottari Dasha tree.

    Body:
        dob   : "YYYY-MM-DD"
        tob   : "HH:MM"
        place : "City, State, Country"

    Returns full Mahadasha → Antardasha → Pratyantardasha tree
    with exact start/end dates, plus the currently active period.
    """
    try:
        result = calculate_dasha(data.dob, data.tob, data.place)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dasha calculation error: {str(e)}")
