from pydantic import BaseModel, field_validator
from datetime import date, time as time_type
from typing import Optional, Literal


class BirthData(BaseModel):
    dob: str        # "2004-02-28"
    tob: str        # "01:15"
    place: str      # "Kochi, Kerala, India"

    @field_validator("dob")
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("dob must be in YYYY-MM-DD format")
        return v

    @field_validator("tob")
    @classmethod
    def validate_time(cls, v: str) -> str:
        try:
            time_type.fromisoformat(v)
        except ValueError:
            raise ValueError("tob must be in HH:MM or HH:MM:SS format")
        return v


class DivisionalRequest(BirthData):
    """Extends BirthData with a chart_type field for divisional charts."""
    chart_type: Literal["D2", "D9", "D10", "D30"] = "D9"


# ── Chart Response models ────────────────────────────────────────────────────

class LagnaInfo(BaseModel):
    sign: int           # 0 = Mesha … 11 = Meena
    sign_name: str
    degree: float


class PlanetInfo(BaseModel):
    id: str             # "Su", "Mo", "Ma" …
    name: str           # "Surya", "Chandra" …
    sign: int
    sign_name: str
    degree: float       # degree within sign (0–29.99)
    absolute_lon: float # full sidereal longitude (0–359.99)
    nakshatra: str
    pada: int           # 1–4
    house: int          # 1–12 from Lagna
    retrograde: bool
    speed: float        # deg/day — negative = retrograde


class HouseInfo(BaseModel):
    house: int
    sign: int
    sign_name: str


class MetaInfo(BaseModel):
    ayanamsha: str
    ayanamsha_value: float
    latitude: float
    longitude: float
    timezone: str
    julian_day: float
    utc_time: str


class YogaInfo(BaseModel):
    name: str
    description: str
    interpretation: str


class ChartResponse(BaseModel):
    lagna: LagnaInfo
    planets: list[PlanetInfo]
    houses: list[HouseInfo]
    meta: MetaInfo
    yogas: list[YogaInfo]
    report: str


# ── Dasha Response models (5 levels) ────────────────────────────────────────

class PranaPeriod(BaseModel):
    lord: str
    lord_name: str
    start_date: str
    end_date: str
    duration_years: float


class SookshmaPeriod(BaseModel):
    lord: str
    lord_name: str
    start_date: str
    end_date: str
    duration_years: float
    pranadasha: list[PranaPeriod]


class PratyantarPeriod(BaseModel):
    lord: str
    lord_name: str
    start_date: str
    end_date: str
    duration_years: float
    sookshmadasha: list[SookshmaPeriod]


class AntarPeriod(BaseModel):
    lord: str
    lord_name: str
    start_date: str
    end_date: str
    duration_years: float
    pratyantardasha: list[PratyantarPeriod]


class MahaPeriod(BaseModel):
    lord: str
    lord_name: str
    start_date: str
    end_date: str
    duration_years: float
    antardasha: list[AntarPeriod]


class CurrentPeriodInfo(BaseModel):
    mahadasha: Optional[PranaPeriod] = None
    antardasha: Optional[PranaPeriod] = None
    pratyantardasha: Optional[PranaPeriod] = None
    sookshmadasha: Optional[PranaPeriod] = None
    pranadasha: Optional[PranaPeriod] = None


class DashaResponse(BaseModel):
    moon_nakshatra: str
    moon_pada: int
    starting_lord: str
    starting_lord_name: str
    balance_at_birth_years: float
    mahadasha: list[MahaPeriod]
    current_period: CurrentPeriodInfo


# ── Life Report models ───────────────────────────────────────────────────────

class ReportSection(BaseModel):
    summary: str
    key_factors: list[str]


class LifeReportResponse(BaseModel):
    health: ReportSection
    career: ReportSection
    relationships: ReportSection
    spirituality: ReportSection
    current_period_summary: ReportSection
