"""
app/schemas/ghat.py
────────────────────
Pydantic schemas for ghats, readings, data sources, and CPCB thresholds.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Data Source ───────────────────────────────────────────────────────────────

class DataSourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    publisher: Optional[str] = None
    report_year: Optional[int] = None
    url: Optional[str] = None
    pdf_page: Optional[str] = None
    notes: Optional[str] = None


# ── Water Quality Reading ─────────────────────────────────────────────────────

class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ghat_id: int
    sampling_date: datetime
    dissolved_oxygen: Optional[float] = Field(None, description="mg/L")
    bod: Optional[float] = Field(None, description="mg/L")
    ph: Optional[float] = None
    fecal_coliform: Optional[float] = Field(None, description="MPN/100mL")
    total_coliform: Optional[float] = Field(None, description="MPN/100mL")
    nitrate: Optional[float] = Field(None, description="mg/L")
    turbidity: Optional[float] = Field(None, description="NTU")
    conductivity: Optional[float] = Field(None, description="µS/cm")
    temperature: Optional[float] = Field(None, description="°C")
    is_verified: bool
    notes: Optional[str] = None
    source: Optional[DataSourceOut] = None


class ReadingCreate(BaseModel):
    ghat_id: int
    sampling_date: datetime
    source_id: Optional[int] = None
    dissolved_oxygen: Optional[float] = None
    bod: Optional[float] = None
    ph: Optional[float] = None
    fecal_coliform: Optional[float] = None
    total_coliform: Optional[float] = None
    nitrate: Optional[float] = None
    turbidity: Optional[float] = None
    conductivity: Optional[float] = None
    temperature: Optional[float] = None
    is_verified: bool = False
    notes: Optional[str] = None


# ── Ghat ─────────────────────────────────────────────────────────────────────

class GhatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    name_hi: Optional[str] = None
    slug: str
    location_description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str


class GhatDetail(GhatOut):
    """Ghat with its most recent readings."""
    latest_readings: List[ReadingOut] = []
    total_readings: int = 0


# ── CPCB Threshold ────────────────────────────────────────────────────────────

class CPCBThresholdOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parameter: str
    water_class: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: str
    description: Optional[str] = None
