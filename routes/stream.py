from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
from models.session_store import SessionStore

stream_router = APIRouter()

@stream_router.get("/api/stream")
async def stream(request: Request):
    sessionId = request.query_params["sessionId"]
    session_store = SessionStore()
    session = session_store.find_or_create(sessionId)
    session.create_queue()
    session_queue = session.get_queue()
    
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    print(f"Client {sessionId} disconnected")
                    break

                # Wait for the next chunk to appear in the queue
                chunk = await session_queue.get()
                print("streaming chunk", "begin " + chunk + " end")
                yield f"data: {chunk}\n\n"
        except asyncio.CancelledError:
            print(f"Streaming cancelled for session {sessionId}")
        finally:
            print(f"Cleaned up session queue: {sessionId}")

    return StreamingResponse(event_generator(), media_type="text/event-stream")