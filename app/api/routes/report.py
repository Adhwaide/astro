"""
api/routes/report.py
─────────────────────
POST /api/report  →  structured life report (health, career, relationships, etc.)
"""

from fastapi import APIRouter, HTTPException
from app.models.request import BirthData
from app.core.calculator import calculate_chart
from app.core.dashas import calculate_dasha
from app.core.report import generate_life_report

router = APIRouter()


@router.post("/report")
async def get_report(data: BirthData):
    """
    Generate a structured life report.

    Body:
        dob   : "YYYY-MM-DD"
        tob   : "HH:MM"
        place : "City, State, Country"

    Returns structured JSON with sections:
    health, career, relationships, spirituality, current_period_summary
    """
    try:
        chart = calculate_chart(data.dob, data.tob, data.place)
        dasha = calculate_dasha(data.dob, data.tob, data.place)
        report = generate_life_report(chart, dasha)
        return report
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")
