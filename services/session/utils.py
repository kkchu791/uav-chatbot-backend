import uuid
from fastapi import Request, Response

def ensure_session_cookie(request: Request, response: Response) -> str:
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
    return session_id