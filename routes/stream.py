from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from models.session_registry import session_registry
from usecases.stream import stream_events

stream_router = APIRouter()

@stream_router.get("/api/stream")
async def stream(request: Request):
    session_id = request.query_params["sessionId"]
    session = session_registry.find_or_create(session_id)
    event_generator = await stream_events(session, request)
    return StreamingResponse(event_generator(), media_type="text/event-stream")