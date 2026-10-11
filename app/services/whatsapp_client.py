"""
app/services/whatsapp_client.py
────────────────────────────────
Official Meta WhatsApp Cloud API client.

IMPORTANT:
  - When WHATSAPP_DRY_RUN=true (the default), no HTTP calls are made to Meta.
  - Dry-run messages are clearly labelled as simulated and never reported as delivered.
  - Secrets are never logged.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Dict, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.exceptions import WhatsAppError
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


class WhatsAppClient:
    """
    Thin wrapper around Meta Graph API v{version}/messages.
    All sends go through `send_template_message`.
    """

    def __init__(self):
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
            timeout=_TIMEOUT,
        )

    async def aclose(self):
        await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def send_template_message(
        self,
        to: str,
        template_name: str,
        language_code: str,
        components: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Send a pre-approved WhatsApp template message.
        Returns the Meta API response dict.
        Raises WhatsAppError on API failure.
        """
        if settings.WHATSAPP_DRY_RUN:
            logger.info(
                "[DRY RUN] Would send WhatsApp template",
                to="[PHONE REDACTED]",
                template=template_name,
                language=language_code,
            )
            return {
                "dry_run": True,
                "messages": [{"id": f"dry_run_{to}_{template_name}"}],
            }

        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
            },
        }
        if components:
            payload["template"]["components"] = components

        response = await self._client.post(
            settings.whatsapp_messages_url,
            json=payload,
        )

        if response.status_code not in (200, 201):
            logger.error(
                "WhatsApp API error",
                status=response.status_code,
                # Do not log the full response body — it may contain PII
            )
            raise WhatsAppError(
                f"Meta API returned {response.status_code}: {response.text[:200]}"
            )

        return response.json()

    async def send_text_message(self, to: str, body: str) -> Dict[str, Any]:
        """
        Send a plain text reply (used for citizen self-service replies).
        Only valid within a 24-hour customer-service window.
        """
        if settings.WHATSAPP_DRY_RUN:
            logger.info("[DRY RUN] Would send text message", to="[PHONE REDACTED]")
            return {"dry_run": True, "messages": [{"id": f"dry_run_text_{to}"}]}

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": body},
        }
        response = await self._client.post(settings.whatsapp_messages_url, json=payload)
        if response.status_code not in (200, 201):
            raise WhatsAppError(f"Meta API returned {response.status_code}")
        return response.json()


# ── Webhook signature validation ─────────────────────────────────────────────

def verify_webhook_signature(raw_body: bytes, x_hub_signature_256: str) -> bool:
    """
    Validate Meta webhook HMAC-SHA256 signature.
    Returns True only if signatures match.
    """
    if not settings.WHATSAPP_APP_SECRET:
        logger.warning("WHATSAPP_APP_SECRET not configured — webhook signature not validated")
        return False

    expected = "sha256=" + hmac.new(
        settings.WHATSAPP_APP_SECRET.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, x_hub_signature_256)
