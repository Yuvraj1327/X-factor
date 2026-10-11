"""
tests/test_auth.py
───────────────────
Tests for admin authentication endpoints.
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.admin import AdminRole, AdminUser


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession) -> AdminUser:
    admin = AdminUser(
        email="test@bmc.gov.in",
        full_name="Test Officer",
        hashed_password=hash_password("SecurePass123!"),
        role=AdminRole.BMC_OFFICER,
        is_active=True,
    )
    db.add(admin)
    await db.flush()
    return admin


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "test@bmc.gov.in",
        "password": "SecurePass123!",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, admin_user):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "test@bmc.gov.in",
        "password": "WrongPassword!",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "nobody@example.com",
        "password": "SomePassword123!",
    })
    assert resp.status_code == 401
    # Both wrong-password and unknown-user return 401 (no enumeration)


@pytest.mark.asyncio
async def test_me_without_token(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 422  # Missing Authorization header


@pytest.mark.asyncio
async def test_me_with_valid_token(client: AsyncClient, admin_user):
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "test@bmc.gov.in",
        "password": "SecurePass123!",
    })
    token = login_resp.json()["access_token"]
    me_resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "test@bmc.gov.in"
    assert "password" not in str(me_resp.json())


@pytest.mark.asyncio
async def test_me_with_invalid_token(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer INVALID"})
    assert resp.status_code == 401
