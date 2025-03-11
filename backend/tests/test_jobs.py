import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_get_jobs():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000/jobs/jobs") as client:
        response = await client.get("/jobs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
