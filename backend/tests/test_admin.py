import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_admin_reset_invalid_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/admin/reset-database", json={"admin_password": "wrongpassword"})
        assert res.status_code == 401
        assert "incorreta" in res.json()["detail"]

@pytest.mark.asyncio
async def test_admin_reset_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/admin/reset-database", json={"admin_password": "blurbang"})
        assert res.status_code == 200
        assert res.json()["status"] == "OK"
