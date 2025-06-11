import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from routes.chat import chat_router
from unittest.mock import patch

app = FastAPI()
app.include_router(chat_router)

@pytest.mark.asyncio
async def test_chat_success():
    with patch("routes.chat.run_chat_stream") as mock_chat, \
         patch("routes.chat.session_registry.find_or_create", return_value=object()), \
         patch("routes.chat.LLMThreadFactory") as mock_factory:

        mock_thread = object()
        mock_factory.return_value.create.return_value = mock_thread

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test", cookies={"session_id": "abc123"}) as ac:
            response = await ac.post("/api/chat", json={"question": "What is UAV?"})

            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
            mock_chat.assert_called_once_with(mock_thread, "What is UAV?")

@pytest.mark.asyncio
async def test_chat_missing_cookie():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/chat", json={"question": "Where am I?"})

        assert response.status_code == 400
        assert response.json() == {"detail": "Missing session ID in cookie"}