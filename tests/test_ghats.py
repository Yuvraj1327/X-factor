"""
tests/test_ghats.py
────────────────────
Tests for ghat list and history endpoints.
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ghat import Ghat, GhatStatus


@pytest_asyncio.fixture
async def sample_ghat(db: AsyncSession) -> Ghat:
    ghat = Ghat(name="Lal Ghat", slug="lal-ghat", status=GhatStatus.ACTIVE)
    db.add(ghat)
    await db.flush()
    return ghat


@pytest.mark.asyncio
async def test_list_ghats(client: AsyncClient, sample_ghat):
    resp = await client.get("/api/v1/ghats")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(g["slug"] == "lal-ghat" for g in data)


@pytest.mark.asyncio
async def test_get_ghat_detail(client: AsyncClient, sample_ghat):
    resp = await client.get(f"/api/v1/ghats/{sample_ghat.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Lal Ghat"
    assert "latest_readings" in data
    assert "total_readings" in data


@pytest.mark.asyncio
async def test_get_nonexistent_ghat(client: AsyncClient):
    resp = await client.get("/api/v1/ghats/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_ghat_history_has_disclaimer(client: AsyncClient, sample_ghat):
    resp = await client.get(f"/api/v1/ghats/{sample_ghat.id}/history")
    assert resp.status_code == 200
    data = resp.json()
    assert "disclaimer" in data
    assert "historical" in data["disclaimer"].lower()


@pytest.mark.asyncio
async def test_analysis_rankings_have_disclaimer(client: AsyncClient, sample_ghat):
    resp = await client.get("/api/v1/analysis/rankings")
    assert resp.status_code == 200
    rankings = resp.json()
    if rankings:
        assert "data_disclaimer" in rankings[0]
        assert "not" in rankings[0]["data_disclaimer"].lower()
