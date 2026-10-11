"""
app/schemas/analysis.py
────────────────────────
Analysis result schemas — explicitly labelled as data-based indicators.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ParameterStatus(BaseModel):
    parameter: str
    value: Optional[float]
    unit: str
    cpcb_min: Optional[float]
    cpcb_max: Optional[float]
    water_class: str
    exceeds_limit: Optional[bool]  # None = no data available
    missing: bool


class GhatRanking(BaseModel):
    """
    Evidence-based risk-priority ranking.
    NOT an official safety certification.
    Rankings are based solely on available historical data.
    """
    ghat_id: int
    ghat_name: str
    ghat_slug: str
    priority_rank: int
    risk_score: float = Field(..., description="Composite score 0-100; higher = more concern")
    risk_label: str = Field(
        ...,
        description="DATA_INDICATOR label: HIGH_PRIORITY | MODERATE_PRIORITY | LOW_PRIORITY | INSUFFICIENT_DATA"
    )
    parameters_assessed: int
    parameters_exceeding: int
    parameters_missing: int
    latest_sampling_date: Optional[datetime]
    data_age_days: Optional[int]
    is_data_fresh: bool
    data_disclaimer: str = (
        "This ranking is based on available historical data only. "
        "It does not certify current water quality or safety. "
        "Sampling date and source are shown for transparency."
    )
    evidence: List[ParameterStatus] = []


class AnalysisSummary(BaseModel):
    total_ghats: int
    ghats_with_data: int
    ghats_without_data: int
    ghats_with_fresh_data: int
    total_readings: int
    date_range_start: Optional[datetime]
    date_range_end: Optional[datetime]
    parameters_available: List[str]
    data_disclaimer: str
    generated_at: datetime


class HistoryPoint(BaseModel):
    sampling_date: datetime
    dissolved_oxygen: Optional[float]
    bod: Optional[float]
    ph: Optional[float]
    fecal_coliform: Optional[float]
    total_coliform: Optional[float]
    source_id: Optional[int]
    is_verified: bool


class GhatHistory(BaseModel):
    ghat_id: int
    ghat_name: str
    readings: List[HistoryPoint]
    total_count: int
    disclaimer: str = (
        "All readings are historical. Do not interpret these as current conditions."
    )
