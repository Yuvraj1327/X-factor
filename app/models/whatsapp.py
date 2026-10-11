"""
app/models/whatsapp.py
───────────────────────
WhatsApp subscribers, consent, messages, and delivery events.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey, Index, Integer,
    String, Text, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class SubscriberStatus(str, enum.Enum):
    ACTIVE = "active"
    UNSUBSCRIBED = "unsubscribed"
    BLOCKED = "blocked"


class MessageStatus(str, enum.Enum):
    QUEUED = "queued"
    SENT = "sent"         # API accepted the request
    DELIVERED = "delivered"  # Meta confirmed device delivery
    READ = "read"
    FAILED = "failed"
    DRY_RUN = "dry_run"   # Simulated — never actually sent


class Subscriber(Base):
    """
    A citizen who has explicitly opted in to receive WhatsApp advisories.
    Phone numbers are stored in E.164 format.
    """
    __tablename__ = "subscribers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phone_e164: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(5), default="hi", nullable=False)
    status: Mapped[SubscriberStatus] = mapped_column(
        Enum(SubscriberStatus), default=SubscriberStatus.ACTIVE, nullable=False
    )

    # Explicit opt-in
    consented_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    unsubscribed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    ghat_preferences: Mapped[List["SubscriberGhat"]] = relationship(
        "SubscriberGhat", back_populates="subscriber", cascade="all, delete-orphan"
    )
    messages: Mapped[List["WhatsAppMessage"]] = relationship(
        "WhatsAppMessage", back_populates="subscriber"
    )

    @property
    def is_opted_in(self) -> bool:
        return (
            self.status == SubscriberStatus.ACTIVE
            and self.consented_at is not None
        )

    def __repr__(self) -> str:
        return f"<Subscriber id={self.id} status={self.status}>"


class SubscriberGhat(Base):
    """Many-to-many: subscriber ↔ ghat."""
    __tablename__ = "subscriber_ghats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subscriber_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subscribers.id", ondelete="CASCADE"), nullable=False
    )
    ghat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ghats.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    subscriber: Mapped["Subscriber"] = relationship("Subscriber", back_populates="ghat_preferences")
    ghat: Mapped["Ghat"] = relationship("Ghat")

    __table_args__ = (
        UniqueConstraint("subscriber_id", "ghat_id", name="uq_subscriber_ghat"),
    )


class WhatsAppMessage(Base):
    """
    Every outgoing message attempt.
    DRY_RUN messages are clearly labelled and were never sent to Meta.
    """
    __tablename__ = "whatsapp_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subscriber_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("subscribers.id", ondelete="SET NULL"), nullable=True
    )
    advisory_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("advisories.id", ondelete="SET NULL"), nullable=True
    )

    recipient_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    template_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    language: Mapped[str] = mapped_column(String(5), nullable=False)
    body_preview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus), default=MessageStatus.QUEUED, nullable=False, index=True
    )
    is_dry_run: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Meta API response fields
    meta_message_id: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, index=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    attempt_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    subscriber: Mapped[Optional["Subscriber"]] = relationship(
        "Subscriber", back_populates="messages"
    )
    advisory: Mapped[Optional["Advisory"]] = relationship(
        "Advisory", back_populates="messages"
    )
    delivery_events: Mapped[List["DeliveryEvent"]] = relationship(
        "DeliveryEvent", back_populates="message", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_wam_advisory_subscriber", "advisory_id", "subscriber_id"),
    )


class DeliveryEvent(Base):
    """
    Webhook delivery-status events from Meta.
    Stored idempotently: the same event ID is never inserted twice.
    """
    __tablename__ = "delivery_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("whatsapp_messages.id", ondelete="CASCADE"), nullable=False
    )
    meta_event_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)  # sent/delivered/read/failed
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    raw_payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    message: Mapped["WhatsAppMessage"] = relationship("WhatsAppMessage", back_populates="delivery_events")


class IncomingMessage(Base):
    """Raw incoming WhatsApp messages from citizens (processed idempotently)."""
    __tablename__ = "incoming_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meta_message_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    from_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    message_type: Mapped[str] = mapped_column(String(30), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
