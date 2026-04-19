"""
api/routes/chart.py
────────────────────
POST /api/chart  →  full D1 planetary positions + lagna
"""

from fastapi import APIRouter, HTTPException
from app.models.request import BirthData, ChartResponse
from app.core.calculator import calculate_chart
from app.core.yogas import detect_yogas, generate_written_report

router = APIRouter()


@router.post("/chart", response_model=ChartResponse)
async def get_chart(data: BirthData):
    """
    Generate Vedic D1 birth chart.

    Body:
        dob   : "YYYY-MM-DD"
        tob   : "HH:MM"
        place : "City, State, Country"

    Returns full lagna, planetary positions, and house signs.
    """
    try:
        result = calculate_chart(data.dob, data.tob, data.place)
        
        # Phase 5: Calculate Yogas and Auto-generate Report
        yogas = detect_yogas(result)
        report = generate_written_report(result, yogas)
        
        result["yogas"] = yogas
        result["report"] = report

        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")
