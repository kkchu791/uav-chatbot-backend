import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from routes.upload import upload_router
from unittest.mock import patch
from io import BytesIO

app = FastAPI()
app.include_router(upload_router)

@pytest.mark.asyncio
async def test_upload_file_success():
    fake_file = BytesIO(b"dummy content")

    with patch("routes.upload.handle_upload") as mock_upload:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test", cookies={"session_id": "abc123"}) as ac:
            response = await ac.post(
                "/api/upload",
                files={"file": ("test.bin", fake_file, "application/octet-stream")}
            )

            assert response.status_code == 200
            assert response.json() == {"message": "File parsed and stored"}
            mock_upload.assert_called_once()

@pytest.mark.asyncio
async def test_upload_file_missing_cookie():
    fake_file = BytesIO(b"dummy content")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/upload",
            files={"file": ("test.bin", fake_file, "application/octet-stream")}
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Missing session ID in cookie"}