"""
app/api/v1/whatsapp.py
───────────────────────
WhatsApp webhook — verification and incoming-message processing.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.session import get_db
from app.repositories.whatsapp_repo import WhatsAppRepository
from app.services.citizen_service import handle_citizen_message
from app.services.whatsapp_client import WhatsAppClient, verify_webhook_signature

settings = get_settings()
logger = get_logger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Webhook"])


# ── GET /whatsapp/webhook — Meta verification challenge ───────────────────────

@router.get("/webhook", summary="Meta webhook verification")
async def webhook_verify(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified")
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Webhook verification failed")


# ── POST /whatsapp/webhook — Incoming messages and delivery updates ────────────

@router.post("/webhook", status_code=200, summary="Incoming WhatsApp messages")
async def webhook_receive(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handles:
    - Incoming citizen messages → citizen_service
    - Delivery-status updates → update message records (idempotent)

    Signature is validated using WHATSAPP_APP_SECRET.
    Duplicate events are discarded idempotently.
    """
    raw_body = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")

    if not verify_webhook_signature(raw_body, signature):
        logger.warning("Invalid webhook signature received")
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    wa_repo = WhatsAppRepository(db)
    wa_client = WhatsAppClient()

    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                # ── Incoming messages ─────────────────────────────────────────
                for msg in value.get("messages", []):
                    await _process_incoming(msg, wa_client, wa_repo, db)

                # ── Delivery status updates ───────────────────────────────────
                for status_update in value.get("statuses", []):
                    await _process_status_update(status_update, wa_repo)
    finally:
        await wa_client.aclose()

    # Always return 200 to Meta — failures should not cause redelivery storms
    return {"status": "ok"}


async def _process_incoming(
    msg: dict,
    wa_client: WhatsAppClient,
    wa_repo: WhatsAppRepository,
    db: AsyncSession,
) -> None:
    meta_msg_id = msg.get("id")
    from_phone = msg.get("from")
    msg_type = msg.get("type", "text")
    body = msg.get("text", {}).get("body", "") if msg_type == "text" else ""
    ts_raw = msg.get("timestamp")
    received_at = (
        datetime.fromtimestamp(int(ts_raw), tz=timezone.utc) if ts_raw else datetime.now(timezone.utc)
    )

    if not meta_msg_id or not from_phone:
        return

    # Idempotency — skip already-processed messages
    existing = await wa_repo.get_incoming_by_meta_id(meta_msg_id)
    if existing:
        logger.info("Duplicate incoming message skipped", meta_id=meta_msg_id)
        return

    await wa_repo.create_incoming(
        meta_message_id=meta_msg_id,
        from_phone=from_phone,
        message_type=msg_type,
        body=body,
        received_at=received_at,
        processed=True,
    )

    reply = await handle_citizen_message(from_phone, body, db)
    await wa_client.send_text_message(from_phone, reply)
    logger.info("Citizen message processed", from_phone="[REDACTED]")


async def _process_status_update(status_update: dict, wa_repo: WhatsAppRepository) -> None:
    meta_msg_id = status_update.get("id")
    status_val = status_update.get("status")  # sent / delivered / read / failed
    ts_raw = status_update.get("timestamp")
    event_ts = (
        datetime.fromtimestamp(int(ts_raw), tz=timezone.utc) if ts_raw else datetime.now(timezone.utc)
    )

    if not meta_msg_id or not status_val:
        return

    message = await wa_repo.get_message_by_meta_id(meta_msg_id)
    if not message:
        return  # Unknown message — ignore

    from app.models.whatsapp import MessageStatus
    status_map = {
        "sent": MessageStatus.SENT,
        "delivered": MessageStatus.DELIVERED,
        "read": MessageStatus.READ,
        "failed": MessageStatus.FAILED,
    }
    new_status = status_map.get(status_val)
    if not new_status:
        return

    # Idempotent event storage
    event_id = f"{meta_msg_id}_{status_val}"
    inserted = await wa_repo.record_delivery_event_idempotent(
        message_id=message.id,
        meta_event_id=event_id,
        event_type=status_val,
        event_timestamp=event_ts,
        raw_payload=json.dumps(status_update)[:2000],
    )
    if not inserted:
        return  # Duplicate

    update_kwargs = {}
    if new_status == MessageStatus.DELIVERED:
        update_kwargs["delivered_at"] = event_ts
    elif new_status == MessageStatus.READ:
        update_kwargs["read_at"] = event_ts
    elif new_status == MessageStatus.FAILED:
        errors = status_update.get("errors", [{}])
        update_kwargs["failed_at"] = event_ts
        update_kwargs["error_code"] = str(errors[0].get("code", ""))
        update_kwargs["error_message"] = errors[0].get("message", "")[:255]

    await wa_repo.update_message_status(message, new_status, **update_kwargs)
