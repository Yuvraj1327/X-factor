"""
app/schemas/advisory.py
────────────────────────
Advisory create/update/response schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.advisory import AdvisoryLanguage, AdvisoryStatus


class AdvisoryCreate(BaseModel):
    ghat_id: int
    title_en: str = Field(..., min_length=5, max_length=255)
    title_hi: Optional[str] = Field(None, max_length=255)
    body_en: str = Field(..., min_length=20)
    body_hi: Optional[str] = None
    recommended_action_en: Optional[str] = None
    recommended_action_hi: Optional[str] = None
    reading_ids: Optional[List[int]] = Field(
        None, description="Water-quality reading IDs used as evidence"
    )
    sampling_date: Optional[datetime] = None
    source_references: Optional[List[str]] = None
    explanation: Optional[str] = None
    language: AdvisoryLanguage = AdvisoryLanguage.BOTH


class AdvisoryUpdate(BaseModel):
    title_en: Optional[str] = Field(None, min_length=5, max_length=255)
    title_hi: Optional[str] = Field(None, max_length=255)
    body_en: Optional[str] = None
    body_hi: Optional[str] = None
    recommended_action_en: Optional[str] = None
    recommended_action_hi: Optional[str] = None
    reading_ids: Optional[List[int]] = None
    sampling_date: Optional[datetime] = None
    source_references: Optional[List[str]] = None
    explanation: Optional[str] = None
    language: Optional[AdvisoryLanguage] = None


class AdvisoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ghat_id: int
    status: AdvisoryStatus
    language: AdvisoryLanguage
    title_en: str
    title_hi: Optional[str] = None
    body_en: str
    body_hi: Optional[str] = None
    recommended_action_en: Optional[str] = None
    recommended_action_hi: Optional[str] = None
    sampling_date: Optional[datetime] = None
    explanation: Optional[str] = None
    approved_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    recipients_count: int
    delivered_count: int
    failed_count: int
    created_by_id: int
    approved_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class DeliveryStatusOut(BaseModel):
    advisory_id: int
    recipients_count: int
    sent_count: int
    delivered_count: int
    read_count: int
    failed_count: int
    dry_run_count: int
