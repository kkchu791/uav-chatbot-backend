from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes.chat import chat_router
from routes.upload import upload_router
from models.session_store import session_store

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    session_store.load_sessions()
    yield
    session_store.save_sessions()

# Include routers
app.include_router(chat_router)
app.include_router(upload_router)
