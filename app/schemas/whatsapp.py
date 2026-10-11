"""
app/schemas/whatsapp.py
────────────────────────
WhatsApp subscriber and message schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SubscriberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone_e164: str
    language: str
    status: str
    consented_at: Optional[datetime] = None
    created_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipient_phone: str
    template_name: Optional[str] = None
    language: str
    status: str
    is_dry_run: bool
    meta_message_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    advisory_id: Optional[int] = None
    created_at: datetime


class WebhookVerifyParams(BaseModel):
    hub_mode: str = Field(..., alias="hub.mode")
    hub_verify_token: str = Field(..., alias="hub.verify_token")
    hub_challenge: str = Field(..., alias="hub.challenge")

    model_config = ConfigDict(populate_by_name=True)
