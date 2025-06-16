from fastapi import APIRouter, Request, Response
import uuid

session_router = APIRouter()

@session_router.get("/api/session")
async def session(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,
            samesite="strict",
            max_age=60 * 60 * 24
        )
    return {"status": "OK"}