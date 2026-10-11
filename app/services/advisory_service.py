"""
app/services/advisory_service.py
──────────────────────────────────
Advisory workflow: create → approve → send.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import (
    AdvisoryStateError,
    ForbiddenError,
    NotFoundError,
    StaleDataError,
)
from app.core.logging import get_logger
from app.models.advisory import Advisory, AdvisoryStatus
from app.models.admin import AdminUser, AdminRole
from app.repositories.advisory_repo import AdvisoryRepository
from app.repositories.ghat_repo import GhatRepository
from app.repositories.whatsapp_repo import WhatsAppRepository
from app.schemas.advisory import AdvisoryCreate, AdvisoryOut, AdvisoryUpdate, DeliveryStatusOut
from app.services.whatsapp_client import WhatsAppClient
from app.models.whatsapp import MessageStatus

settings = get_settings()
logger = get_logger(__name__)


class AdvisoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AdvisoryRepository(db)
        self.ghat_repo = GhatRepository(db)
        self.wa_repo = WhatsAppRepository(db)

    async def create_draft(self, data: AdvisoryCreate, admin: AdminUser) -> Advisory:
        ghat = await self.ghat_repo.get_ghat(data.ghat_id)
        if not ghat:
            raise NotFoundError(f"Ghat {data.ghat_id} not found")

        reading_ids_str = None
        if data.reading_ids:
            reading_ids_str = ",".join(str(i) for i in data.reading_ids)

        source_refs_str = None
        if data.source_references:
            source_refs_str = json.dumps(data.source_references)

        advisory = await self.repo.create(
            ghat_id=data.ghat_id,
            created_by_id=admin.id,
            title_en=data.title_en,
            title_hi=data.title_hi,
            body_en=data.body_en,
            body_hi=data.body_hi,
            recommended_action_en=data.recommended_action_en,
            recommended_action_hi=data.recommended_action_hi,
            language=data.language,
            reading_ids=reading_ids_str,
            sampling_date=data.sampling_date,
            source_references=source_refs_str,
            explanation=data.explanation,
            status=AdvisoryStatus.DRAFT,
        )
        logger.info("Advisory draft created", advisory_id=advisory.id, admin_id=admin.id)
        return advisory

    async def update_draft(
        self, advisory_id: int, data: AdvisoryUpdate, admin: AdminUser
    ) -> Advisory:
        advisory = await self.repo.get(advisory_id)
        if not advisory:
            raise NotFoundError(f"Advisory {advisory_id} not found")
        if advisory.status != AdvisoryStatus.DRAFT:
            raise AdvisoryStateError("Only draft advisories can be edited")

        updates = data.model_dump(exclude_unset=True)
        if "reading_ids" in updates and updates["reading_ids"] is not None:
            updates["reading_ids"] = ",".join(str(i) for i in updates["reading_ids"])
        if "source_references" in updates and updates["source_references"] is not None:
            updates["source_references"] = json.dumps(updates["source_references"])

        return await self.repo.update(advisory, updates)

    async def approve(self, advisory_id: int, admin: AdminUser) -> Advisory:
        """Only BMC officers and super admins can approve."""
        if admin.role not in (AdminRole.BMC_OFFICER, AdminRole.SUPER_ADMIN):
            raise ForbiddenError("Only BMC Officers can approve advisories")

        advisory = await self.repo.get(advisory_id)
        if not advisory:
            raise NotFoundError(f"Advisory {advisory_id} not found")
        if not advisory.can_be_approved():
            raise AdvisoryStateError(
                f"Advisory is in '{advisory.status}' state and cannot be approved"
            )

        # Block approval if data is stale
        if advisory.sampling_date:
            age_days = (datetime.now(timezone.utc) - advisory.sampling_date.replace(
                tzinfo=timezone.utc if advisory.sampling_date.tzinfo is None else advisory.sampling_date.tzinfo
            )).days
            if age_days > settings.DATA_FRESHNESS_THRESHOLD_DAYS:
                raise StaleDataError(
                    f"Sampling date is {age_days} days old (threshold: "
                    f"{settings.DATA_FRESHNESS_THRESHOLD_DAYS} days). "
                    "Update with fresh readings before approving."
                )

        updates = {
            "status": AdvisoryStatus.APPROVED,
            "approved_by_id": admin.id,
            "approved_at": datetime.now(timezone.utc),
        }
        advisory = await self.repo.update(advisory, updates)
        logger.info("Advisory approved", advisory_id=advisory.id, approved_by=admin.id)
        return advisory

    async def send_advisory(self, advisory_id: int, admin: AdminUser) -> Advisory:
        """Send an approved advisory to all opted-in subscribers of the ghat."""
        advisory = await self.repo.get(advisory_id)
        if not advisory:
            raise NotFoundError(f"Advisory {advisory_id} not found")
        if not advisory.can_be_sent():
            raise AdvisoryStateError(
                f"Advisory must be in APPROVED state to send. Current: {advisory.status}"
            )

        # Prevent duplicate sends
        if advisory.sent_at:
            raise AdvisoryStateError("Advisory has already been sent")

        ghat = await self.ghat_repo.get_ghat(advisory.ghat_id)
        subscribers = await self.wa_repo.get_opted_in_subscribers_for_ghat(advisory.ghat_id)

        if not subscribers:
            logger.info(
                "No opted-in subscribers for ghat",
                ghat_id=advisory.ghat_id,
                advisory_id=advisory_id,
            )

        wa_client = WhatsAppClient()
        sent = 0
        failed = 0

        for subscriber in subscribers:
            try:
                template = (
                    settings.WHATSAPP_TEMPLATE_NAME_HI
                    if subscriber.language == "hi"
                    else settings.WHATSAPP_TEMPLATE_NAME_EN
                )
                lang_code = "hi" if subscriber.language == "hi" else "en"
                resp = await wa_client.send_template_message(
                    to=subscriber.phone_e164,
                    template_name=template,
                    language_code=lang_code,
                )
                meta_id = None
                is_dry = resp.get("dry_run", settings.WHATSAPP_DRY_RUN)
                if not is_dry and "messages" in resp:
                    meta_id = resp["messages"][0].get("id")

                await self.wa_repo.create_message(
                    subscriber_id=subscriber.id,
                    advisory_id=advisory.id,
                    recipient_phone=subscriber.phone_e164,
                    template_name=template,
                    language=lang_code,
                    status=MessageStatus.DRY_RUN if is_dry else MessageStatus.SENT,
                    is_dry_run=is_dry,
                    meta_message_id=meta_id,
                    sent_at=datetime.now(timezone.utc) if not is_dry else None,
                )
                sent += 1
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Failed to send advisory message",
                    advisory_id=advisory_id,
                    error=str(exc),
                )
                await self.wa_repo.create_message(
                    subscriber_id=subscriber.id,
                    advisory_id=advisory.id,
                    recipient_phone=subscriber.phone_e164,
                    status=MessageStatus.FAILED,
                    is_dry_run=settings.WHATSAPP_DRY_RUN,
                    language=subscriber.language,
                    error_message=str(exc)[:255],
                    failed_at=datetime.now(timezone.utc),
                )
                failed += 1

        await wa_client.aclose()

        advisory = await self.repo.update(advisory, {
            "status": AdvisoryStatus.SENT,
            "sent_at": datetime.now(timezone.utc),
            "recipients_count": len(subscribers),
            "failed_count": failed,
        })
        logger.info(
            "Advisory send complete",
            advisory_id=advisory_id,
            sent=sent,
            failed=failed,
            dry_run=settings.WHATSAPP_DRY_RUN,
        )
        return advisory

    async def get_delivery_status(self, advisory_id: int) -> DeliveryStatusOut:
        advisory = await self.repo.get(advisory_id)
        if not advisory:
            raise NotFoundError(f"Advisory {advisory_id} not found")

        stats = await self.repo.get_delivery_stats(advisory_id)
        return DeliveryStatusOut(
            advisory_id=advisory_id,
            recipients_count=advisory.recipients_count,
            sent_count=stats.get(MessageStatus.SENT, 0),
            delivered_count=stats.get(MessageStatus.DELIVERED, 0),
            read_count=stats.get(MessageStatus.READ, 0),
            failed_count=stats.get(MessageStatus.FAILED, 0),
            dry_run_count=stats.get(MessageStatus.DRY_RUN, 0),
        )
