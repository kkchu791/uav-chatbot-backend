import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from routes.session import session_router

app = FastAPI()
app.include_router(session_router)

@pytest.mark.asyncio
async def test_session_sets_cookie_and_returns_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/session")

        assert response.status_code == 200
        json_data = response.json()
        assert "session_id" in json_data
        assert isinstance(json_data["session_id"], str)
        assert "set-cookie" in response.headers