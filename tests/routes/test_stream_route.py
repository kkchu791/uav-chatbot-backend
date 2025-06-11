import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from routes.stream import stream_router
from unittest.mock import patch

app = FastAPI()
app.include_router(stream_router)

async def fake_event_generator():
    yield "data: hello\n\n"
    yield "data: world\n\n"

async def fake_stream_events(session, request):
    return lambda: fake_event_generator()

@pytest.mark.asyncio
async def test_stream_with_real_async_generator():
    with patch("routes.stream.stream_events", fake_stream_events), \
         patch("routes.stream.session_registry.find_or_create", return_value=object()):

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test", cookies={"session_id": "abc123"}) as ac:
            response = await ac.get("/api/stream")

            assert response.status_code == 200
            assert "data: hello" in response.text
            assert "data: world" in response.text