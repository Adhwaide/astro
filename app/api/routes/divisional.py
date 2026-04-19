"""
api/routes/divisional.py
─────────────────────────
POST /api/divisional  →  divisional chart (D2, D9, D10, D30)
"""

from fastapi import APIRouter, HTTPException
from app.models.request import DivisionalRequest
from app.core.divisional import calculate_divisional

router = APIRouter()


@router.post("/divisional")
async def get_divisional(data: DivisionalRequest):
    """
    Generate a Vedic divisional chart.

    Body:
        dob        : "YYYY-MM-DD"
        tob        : "HH:MM"
        place      : "City, State, Country"
        chart_type : "D2" | "D9" | "D10" | "D30"

    Returns planet positions in the divisional chart with same structure as /api/chart.
    """
    try:
        result = calculate_divisional(data.dob, data.tob, data.place, data.chart_type)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Divisional chart error: {str(e)}")
