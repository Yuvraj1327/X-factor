"""
app/api/v1/admin.py
────────────────────
BMC Admin Dashboard — protected endpoints.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, require_approver
from app.analysis.engine import build_summary, rank_ghats
from app.database.session import get_db
from app.models.admin import AdminUser
from app.models.advisory import AdvisoryStatus
from app.repositories.advisory_repo import AdvisoryRepository
from app.repositories.ghat_repo import GhatRepository
from app.repositories.whatsapp_repo import WhatsAppRepository
from app.schemas.advisory import AdvisoryCreate, AdvisoryOut, AdvisoryUpdate, DeliveryStatusOut
from app.schemas.whatsapp import MessageOut
from app.services.advisory_service import AdvisoryService

router = APIRouter(prefix="/admin", tags=["BMC Admin"])


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard", summary="Admin dashboard summary")
async def dashboard(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    ghat_repo = GhatRepository(db)
    advisory_repo = AdvisoryRepository(db)

    ghats = await ghat_repo.list_ghats()
    ghats_data = []
    for g in ghats:
        reading = await ghat_repo.get_latest_reading(g.id)
        rd = None
        if reading:
            rd = {
                "sampling_date": reading.sampling_date,
                "dissolved_oxygen": reading.dissolved_oxygen,
                "bod": reading.bod,
                "ph": reading.ph,
                "fecal_coliform": reading.fecal_coliform,
                "total_coliform": reading.total_coliform,
                "nitrate": reading.nitrate,
                "turbidity": reading.turbidity,
            }
        ghats_data.append({"ghat_id": g.id, "ghat_name": g.name, "ghat_slug": g.slug, "latest_reading": rd})

    thresholds = await ghat_repo.get_thresholds_as_dict()
    rankings = rank_ghats(ghats_data, thresholds)
    top_priority = rankings[:3] if rankings else []

    pending_advisories = await advisory_repo.list_all(status=AdvisoryStatus.DRAFT, limit=5)
    recent_sent = await advisory_repo.list_all(status=AdvisoryStatus.SENT, limit=5)

    return {
        "admin": {"id": admin.id, "email": admin.email, "role": admin.role},
        "ghat_count": len(ghats),
        "top_priority_ghats": [
            {"ghat_id": r.ghat_id, "ghat_name": r.ghat_name, "risk_label": r.risk_label}
            for r in top_priority
        ],
        "pending_advisories": len(pending_advisories),
        "recent_sent_advisories": len(recent_sent),
        "disclaimer": (
            "Rankings are data-based priority indicators only, "
            "not official safety certifications."
        ),
    }


# ── Advisory CRUD ─────────────────────────────────────────────────────────────

@router.get("/advisories", response_model=List[AdvisoryOut], summary="List advisories")
async def list_advisories(
    advisory_status: Optional[str] = Query(None, alias="status"),
    ghat_id: Optional[int] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    repo = AdvisoryRepository(db)
    status_filter = AdvisoryStatus(advisory_status) if advisory_status else None
    return await repo.list_all(status=status_filter, ghat_id=ghat_id, limit=limit, offset=offset)


@router.post("/advisories", response_model=AdvisoryOut, status_code=201, summary="Create draft advisory")
async def create_advisory(
    data: AdvisoryCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdvisoryService(db)
    return await service.create_draft(data, admin)


@router.get("/advisories/{advisory_id}", response_model=AdvisoryOut, summary="Get advisory detail")
async def get_advisory(
    advisory_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    repo = AdvisoryRepository(db)
    advisory = await repo.get(advisory_id)
    if not advisory:
        raise HTTPException(status_code=404, detail="Advisory not found")
    return advisory


@router.patch("/advisories/{advisory_id}", response_model=AdvisoryOut, summary="Update draft advisory")
async def update_advisory(
    advisory_id: int,
    data: AdvisoryUpdate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdvisoryService(db)
    return await service.update_draft(advisory_id, data, admin)


@router.post("/advisories/{advisory_id}/approve", response_model=AdvisoryOut, summary="Approve advisory")
async def approve_advisory(
    advisory_id: int,
    admin: AdminUser = Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """Approve a draft advisory. Only BMC Officers and Super Admins can approve."""
    service = AdvisoryService(db)
    return await service.approve(advisory_id, admin)


@router.post("/advisories/{advisory_id}/send", response_model=AdvisoryOut, summary="Send approved advisory")
async def send_advisory(
    advisory_id: int,
    admin: AdminUser = Depends(require_approver),
    db: AsyncSession = Depends(get_db),
):
    """Send an approved advisory to opted-in subscribers."""
    service = AdvisoryService(db)
    return await service.send_advisory(advisory_id, admin)


@router.get("/advisories/{advisory_id}/delivery-status", response_model=DeliveryStatusOut)
async def delivery_status(
    advisory_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdvisoryService(db)
    return await service.get_delivery_status(advisory_id)


# ── WhatsApp message history ──────────────────────────────────────────────────

@router.get("/whatsapp/messages", response_model=List[MessageOut], summary="WhatsApp message history")
async def whatsapp_messages(
    advisory_id: Optional[int] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    repo = WhatsAppRepository(db)
    return await repo.list_messages(advisory_id=advisory_id, limit=limit, offset=offset)
