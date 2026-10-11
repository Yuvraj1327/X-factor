"""
app/models/advisory.py
───────────────────────
Advisory, approval history, and related models.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class AdvisoryStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    SENT = "sent"
    ARCHIVED = "archived"


class AdvisoryLanguage(str, enum.Enum):
    EN = "en"
    HI = "hi"
    BOTH = "both"


class Advisory(Base):
    """
    An official advisory created by BMC about a ghat's water quality.
    Must be approved by an authorized officer before it can be sent.
    """
    __tablename__ = "advisories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ghat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ghats.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("admin_users.id", ondelete="RESTRICT"), nullable=False
    )
    approved_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("admin_users.id", ondelete="RESTRICT"), nullable=True
    )

    status: Mapped[AdvisoryStatus] = mapped_column(
        Enum(AdvisoryStatus), default=AdvisoryStatus.DRAFT, nullable=False, index=True
    )
    language: Mapped[AdvisoryLanguage] = mapped_column(
        Enum(AdvisoryLanguage), default=AdvisoryLanguage.BOTH, nullable=False
    )

    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    title_hi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    body_en: Mapped[str] = mapped_column(Text, nullable=False)
    body_hi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_action_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_action_hi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Evidence linking
    reading_ids: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True,
        comment="Comma-separated WaterQualityReading IDs used as evidence"
    )
    sampling_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_references: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="JSON array of source reference strings"
    )
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Approval tracking
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Delivery statistics (denormalised for quick reads)
    recipients_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    delivered_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    ghat: Mapped["Ghat"] = relationship("Ghat", back_populates="advisories")
    created_by: Mapped["AdminUser"] = relationship(
        "AdminUser", back_populates="advisories_created", foreign_keys=[created_by_id]
    )
    approved_by: Mapped[Optional["AdminUser"]] = relationship(
        "AdminUser", back_populates="advisories_approved", foreign_keys=[approved_by_id]
    )
    messages: Mapped[List["WhatsAppMessage"]] = relationship(
        "WhatsAppMessage", back_populates="advisory"
    )

    def can_be_approved(self) -> bool:
        return self.status == AdvisoryStatus.DRAFT

    def can_be_sent(self) -> bool:
        return self.status == AdvisoryStatus.APPROVED

    def __repr__(self) -> str:
        return f"<Advisory id={self.id} status={self.status} ghat_id={self.ghat_id}>"
