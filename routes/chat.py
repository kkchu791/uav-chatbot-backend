from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest
from usecases.chat import run_chat_stream
from models.session_registry import session_registry
from services.llm.thread_factory import LLMThreadFactory

chat_router = APIRouter()

@chat_router.post("/api/chat")
def chat(body: ChatRequest):
    try:
        question = body.question
        session_id = body.session_id
        print(session_id, 'session_id')
        session = session_registry.find_or_create(session_id)
        print(session, 'session')
        factory = LLMThreadFactory()
        provider = body.provider or 'openai'
        thread = factory.create(provider, session)

        run_chat_stream(thread, question)

        return {"status": "ok"}
    except Exception as e:
        print("Chat error:", e)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
