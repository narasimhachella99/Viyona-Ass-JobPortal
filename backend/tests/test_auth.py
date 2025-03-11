import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000/auth/auth/register") as client:
        response = await client.post(
            "/auth/register",
            json={"email": "kumar@example.com", "password": "123"}
        )
    assert response.status_code == 201
    assert response.json()["message"] == "User registered successfully"

@pytest.mark.asyncio
async def test_login_user(): 
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000/auth/auth/login") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "kumar@example.com", "password": "123"}
        )
    assert response.status_code == 200
