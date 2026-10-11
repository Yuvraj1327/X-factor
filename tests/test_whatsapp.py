"""
tests/test_whatsapp.py
───────────────────────
Tests for WhatsApp webhook, subscription, and dry-run mode.
"""
from __future__ import annotations

import hashlib
import hmac
import json

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.whatsapp import Subscriber, SubscriberStatus
from app.services.whatsapp_client import verify_webhook_signature

settings = get_settings()


class TestWebhookVerification:
    @pytest.mark.asyncio
    async def test_valid_verify_token(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/whatsapp/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN or "test_token",
                "hub.challenge": "abc123",
            },
        )
        # If WHATSAPP_WEBHOOK_VERIFY_TOKEN matches, should return challenge
        if settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
            assert resp.status_code == 200
            assert resp.text == "abc123"

    @pytest.mark.asyncio
    async def test_invalid_verify_token(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/whatsapp/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "WRONG_TOKEN",
                "hub.challenge": "abc123",
            },
        )
        assert resp.status_code == 403


class TestSignatureValidation:
    def test_valid_signature(self):
        secret = "test_secret"
        body = b'{"test": "payload"}'
        sig = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        # Temporarily override the app secret for this test
        import unittest.mock
        with unittest.mock.patch.object(settings, "WHATSAPP_APP_SECRET", secret):
            result = verify_webhook_signature(body, sig)
        assert result is True

    def test_invalid_signature(self):
        secret = "test_secret"
        body = b'{"test": "payload"}'
        import unittest.mock
        with unittest.mock.patch.object(settings, "WHATSAPP_APP_SECRET", secret):
            result = verify_webhook_signature(body, "sha256=invalidsig")
        assert result is False


class TestDryRunMode:
    @pytest.mark.asyncio
    async def test_dry_run_default_is_true(self):
        """Dry-run must be enabled by default to prevent accidental sends."""
        assert settings.WHATSAPP_DRY_RUN is True, (
            "WHATSAPP_DRY_RUN must default to True — "
            "never send to Meta without explicit configuration."
        )


class TestSubscription:
    @pytest.mark.asyncio
    async def test_subscriber_opt_out_respected(self, db: AsyncSession):
        """Unsubscribed users must not receive messages."""
        sub = Subscriber(
            phone_e164="+919876543210",
            language="hi",
            status=SubscriberStatus.UNSUBSCRIBED,
        )
        db.add(sub)
        await db.flush()
        assert not sub.is_opted_in

    @pytest.mark.asyncio
    async def test_subscriber_without_consent_not_opted_in(self, db: AsyncSession):
        """A subscriber without consented_at is not opted in, even if active."""
        sub = Subscriber(
            phone_e164="+919876543211",
            language="hi",
            status=SubscriberStatus.ACTIVE,
            consented_at=None,
        )
        db.add(sub)
        await db.flush()
        assert not sub.is_opted_in


class TestDuplicateWebhookEvents:
    @pytest.mark.asyncio
    async def test_duplicate_delivery_event_skipped(self, db: AsyncSession):
        """Idempotency: the same delivery event must not be inserted twice."""
        from app.repositories.whatsapp_repo import WhatsAppRepository
        from app.models.whatsapp import WhatsAppMessage, MessageStatus
        from datetime import datetime, timezone

        # Create a message record first
        msg = WhatsAppMessage(
            recipient_phone="+919876543212",
            language="hi",
            status=MessageStatus.SENT,
            is_dry_run=False,
            meta_message_id="meta_abc123",
        )
        db.add(msg)
        await db.flush()

        repo = WhatsAppRepository(db)
        ts = datetime.now(timezone.utc)

        result1 = await repo.record_delivery_event_idempotent(
            message_id=msg.id,
            meta_event_id="event_xyz",
            event_type="delivered",
            event_timestamp=ts,
        )
        result2 = await repo.record_delivery_event_idempotent(
            message_id=msg.id,
            meta_event_id="event_xyz",  # Same event ID
            event_type="delivered",
            event_timestamp=ts,
        )
        assert result1 is True
        assert result2 is False  # Duplicate — must be skipped
