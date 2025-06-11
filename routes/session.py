from fastapi import APIRouter, Request, Response
from services.session.utils import ensure_session_cookie

session_router = APIRouter()

@session_router.get("/api/session")
async def session(request: Request, response: Response):
    session_id = ensure_session_cookie(request, response)
    return {"session_id": session_id}