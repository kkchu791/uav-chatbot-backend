from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes.chat import chat_router
from routes.upload import upload_router
from routes.stream import stream_router
from models.session_registry import session_registry
from routes.session import session_router

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    session_registry.load_sessions()
    yield
    session_registry.save_sessions()

# Include routers
app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(stream_router)
app.include_router(session_router)
