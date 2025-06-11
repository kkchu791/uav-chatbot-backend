from services.session.utils import ensure_session_cookie
from fastapi import Request

async def add_session_cookie(request: Request, call_next):
    response = await call_next(request)
    ensure_session_cookie(request, response)
    return response