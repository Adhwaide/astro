"""
main.py
────────
FastAPI application entry point.
Run locally: uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chart, dasha, divisional, report

app = FastAPI(
    title="Jyotisha Engine API",
    description="Vedic astrology calculation backend — D1/D9 charts, Dasha, Yogas, Life Report",
    version="0.3.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# In production, replace "*" with your GitHub Pages URL
# e.g. "https://yourusername.github.io"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(chart.router, prefix="/api")
app.include_router(dasha.router, prefix="/api")
app.include_router(divisional.router, prefix="/api")
app.include_router(report.router, prefix="/api")


@app.get("/health")
async def health():
    """Render.com uses this endpoint to verify the service is alive."""
    return {"status": "ok", "service": "jyotisha-engine"}


@app.get("/")
async def root():
    return {
        "message": "Jyotisha Engine API",
        "docs": "/docs",
        "health": "/health",
        "endpoints": ["/api/chart", "/api/dasha", "/api/divisional", "/api/report"],
    }
