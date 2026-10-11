"""
tests/test_advisory.py
───────────────────────
Tests for advisory creation, approval, stale-data blocking, and send flow.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.admin import AdminRole, AdminUser
from app.models.ghat import Ghat, GhatStatus


@pytest_asyncio.fixture
async def bmc_officer(db: AsyncSession) -> tuple[AdminUser, str]:
    admin = AdminUser(
        email="officer@bmc.gov.in",
        full_name="BMC Officer",
        hashed_password=hash_password("OfficerPass123!"),
        role=AdminRole.BMC_OFFICER,
        is_active=True,
    )
    db.add(admin)
    await db.flush()
    return admin


@pytest_asyncio.fixture
async def data_analyst(db: AsyncSession) -> AdminUser:
    admin = AdminUser(
        email="analyst@bmc.gov.in",
        full_name="Data Analyst",
        hashed_password=hash_password("AnalystPass123!"),
        role=AdminRole.DATA_ANALYST,
        is_active=True,
    )
    db.add(admin)
    await db.flush()
    return admin


@pytest_asyncio.fixture
async def test_ghat(db: AsyncSession) -> Ghat:
    ghat = Ghat(
        name="Bhoj Talaab Ghat",
        slug="bhoj-talaab-ghat",
        status=GhatStatus.ACTIVE,
    )
    db.add(ghat)
    await db.flush()
    return ghat


async def _login(client: AsyncClient, email: str, password: str) -> str:
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_draft_advisory(client: AsyncClient, bmc_officer, test_ghat):
    token = await _login(client, "officer@bmc.gov.in", "OfficerPass123!")
    resp = await client.post(
        "/api/v1/admin/advisories",
        json={
            "ghat_id": test_ghat.id,
            "title_en": "Water Quality Notice",
            "body_en": "This is a test advisory body with sufficient length.",
            "language": "en",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "draft"
    assert data["approved_by_id"] is None


@pytest.mark.asyncio
async def test_approve_changes_status(client: AsyncClient, bmc_officer, test_ghat):
    token = await _login(client, "officer@bmc.gov.in", "OfficerPass123!")
    create_resp = await client.post(
        "/api/v1/admin/advisories",
        json={
            "ghat_id": test_ghat.id,
            "title_en": "Test Advisory",
            "body_en": "Advisory body text for testing approval workflow.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    advisory_id = create_resp.json()["id"]
    approve_resp = await client.post(
        f"/api/v1/admin/advisories/{advisory_id}/approve",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "approved"
    assert approve_resp.json()["approved_at"] is not None


@pytest.mark.asyncio
async def test_data_analyst_cannot_approve(client: AsyncClient, data_analyst, bmc_officer, test_ghat):
    officer_token = await _login(client, "officer@bmc.gov.in", "OfficerPass123!")
    create_resp = await client.post(
        "/api/v1/admin/advisories",
        json={
            "ghat_id": test_ghat.id,
            "title_en": "Analyst Test",
            "body_en": "Testing that analysts cannot approve advisories.",
        },
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    advisory_id = create_resp.json()["id"]

    analyst_token = await _login(client, "analyst@bmc.gov.in", "AnalystPass123!")
    approve_resp = await client.post(
        f"/api/v1/admin/advisories/{advisory_id}/approve",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert approve_resp.status_code == 403


@pytest.mark.asyncio
async def test_stale_data_blocks_approval(client: AsyncClient, bmc_officer, test_ghat):
    """Advisories with sampling dates older than threshold should be rejected at approval."""
    token = await _login(client, "officer@bmc.gov.in", "OfficerPass123!")
    stale_date = (datetime.now(timezone.utc) - timedelta(days=200)).isoformat()

    create_resp = await client.post(
        "/api/v1/admin/advisories",
        json={
            "ghat_id": test_ghat.id,
            "title_en": "Stale Advisory",
            "body_en": "This advisory references outdated water quality data.",
            "sampling_date": stale_date,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    advisory_id = create_resp.json()["id"]
    approve_resp = await client.post(
        f"/api/v1/admin/advisories/{advisory_id}/approve",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert approve_resp.status_code == 422
    assert "stale" in approve_resp.json()["detail"].lower() or "old" in approve_resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_cannot_send_unapproved_advisory(client: AsyncClient, bmc_officer, test_ghat):
    token = await _login(client, "officer@bmc.gov.in", "OfficerPass123!")
    create_resp = await client.post(
        "/api/v1/admin/advisories",
        json={
            "ghat_id": test_ghat.id,
            "title_en": "Draft Only",
            "body_en": "This advisory should not be sendable in draft state.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    advisory_id = create_resp.json()["id"]
    send_resp = await client.post(
        f"/api/v1/admin/advisories/{advisory_id}/send",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert send_resp.status_code == 409
