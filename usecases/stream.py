import asyncio

async def stream_events(session, request):
    queue = session.queue

    async def event_generator():
        try:
            while not await request.is_disconnected():
                try:
                    chunk = await asyncio.wait_for(queue.get(), timeout=30)
                    print("streaming chunk ", chunk)
                    yield f"data: {chunk}\n\n"
                except asyncio.TimeoutError:
                    yield f"data: [ping]\n\n"
        except asyncio.CancelledError:
            print(f"Streaming cancelled for session {session.session_id}")
        finally:
            print(f"Cleaned up session queue: {session.session_id}")

    return event_generator