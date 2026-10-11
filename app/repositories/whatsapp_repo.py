"""
app/repositories/whatsapp_repo.py
───────────────────────────────────
WhatsApp subscriber, message, and event database access.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.whatsapp import (
    DeliveryEvent,
    IncomingMessage,
    MessageStatus,
    Subscriber,
    SubscriberGhat,
    SubscriberStatus,
    WhatsAppMessage,
)


class WhatsAppRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Subscribers ───────────────────────────────────────────────────────────

    async def get_subscriber_by_phone(self, phone: str) -> Optional[Subscriber]:
        result = await self.db.execute(
            select(Subscriber).where(Subscriber.phone_e164 == phone)
        )
        return result.scalar_one_or_none()

    async def get_or_create_subscriber(self, phone: str, language: str = "hi") -> Subscriber:
        sub = await self.get_subscriber_by_phone(phone)
        if not sub:
            sub = Subscriber(phone_e164=phone, language=language)
            self.db.add(sub)
            await self.db.flush()
        return sub

    async def set_consent(self, subscriber: Subscriber) -> Subscriber:
        subscriber.status = SubscriberStatus.ACTIVE
        subscriber.consented_at = datetime.now(timezone.utc)
        await self.db.flush()
        return subscriber

    async def unsubscribe(self, subscriber: Subscriber) -> Subscriber:
        subscriber.status = SubscriberStatus.UNSUBSCRIBED
        subscriber.unsubscribed_at = datetime.now(timezone.utc)
        await self.db.flush()
        return subscriber

    async def get_opted_in_subscribers_for_ghat(self, ghat_id: int) -> List[Subscriber]:
        result = await self.db.execute(
            select(Subscriber)
            .join(SubscriberGhat, SubscriberGhat.subscriber_id == Subscriber.id)
            .where(
                SubscriberGhat.ghat_id == ghat_id,
                Subscriber.status == SubscriberStatus.ACTIVE,
                Subscriber.consented_at.isnot(None),
            )
        )
        return list(result.scalars().all())

    async def add_ghat_preference(self, subscriber_id: int, ghat_id: int) -> None:
        result = await self.db.execute(
            select(SubscriberGhat).where(
                SubscriberGhat.subscriber_id == subscriber_id,
                SubscriberGhat.ghat_id == ghat_id,
            )
        )
        if not result.scalar_one_or_none():
            self.db.add(SubscriberGhat(subscriber_id=subscriber_id, ghat_id=ghat_id))
            await self.db.flush()

    # ── Messages ──────────────────────────────────────────────────────────────

    async def create_message(self, **kwargs) -> WhatsAppMessage:
        msg = WhatsAppMessage(**kwargs)
        self.db.add(msg)
        await self.db.flush()
        return msg

    async def get_message_by_meta_id(self, meta_id: str) -> Optional[WhatsAppMessage]:
        result = await self.db.execute(
            select(WhatsAppMessage).where(WhatsAppMessage.meta_message_id == meta_id)
        )
        return result.scalar_one_or_none()

    async def list_messages(
        self,
        advisory_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[WhatsAppMessage]:
        q = select(WhatsAppMessage)
        if advisory_id:
            q = q.where(WhatsAppMessage.advisory_id == advisory_id)
        q = q.order_by(WhatsAppMessage.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def update_message_status(
        self,
        message: WhatsAppMessage,
        status: MessageStatus,
        **kwargs,
    ) -> WhatsAppMessage:
        message.status = status
        for k, v in kwargs.items():
            setattr(message, k, v)
        await self.db.flush()
        return message

    # ── Delivery events (idempotent) ─────────────────────────────────────────

    async def record_delivery_event_idempotent(
        self,
        message_id: int,
        meta_event_id: str,
        event_type: str,
        event_timestamp: datetime,
        raw_payload: Optional[str] = None,
    ) -> bool:
        """Returns True if newly inserted, False if duplicate."""
        result = await self.db.execute(
            select(DeliveryEvent).where(DeliveryEvent.meta_event_id == meta_event_id)
        )
        if result.scalar_one_or_none():
            return False  # Already processed
        self.db.add(DeliveryEvent(
            message_id=message_id,
            meta_event_id=meta_event_id,
            event_type=event_type,
            event_timestamp=event_timestamp,
            raw_payload=raw_payload,
        ))
        await self.db.flush()
        return True

    # ── Incoming messages ─────────────────────────────────────────────────────

    async def get_incoming_by_meta_id(self, meta_id: str) -> Optional[IncomingMessage]:
        result = await self.db.execute(
            select(IncomingMessage).where(IncomingMessage.meta_message_id == meta_id)
        )
        return result.scalar_one_or_none()

    async def create_incoming(self, **kwargs) -> IncomingMessage:
        msg = IncomingMessage(**kwargs)
        self.db.add(msg)
        await self.db.flush()
        return msg
