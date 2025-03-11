import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_apply_for_job():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000/applications/applications/") as client:
        # First, login to get JWT token
        login_response = await client.post(
            "/auth/login",
            json={"email": "kumar@example.com", "password": "123"}
        )
        token = login_response.json()["token"]

        # Apply for a job using the token
        response = await client.post(
            "/applications/",
            headers={"Authorization": f"Bearer {token}"},
            json={"job_id": 1}
        )

    assert response.status_code == 201
    assert response.json()["status"] == "Pending"
