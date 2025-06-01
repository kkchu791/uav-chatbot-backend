from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest
from services.llm import ask_llm

chat_router = APIRouter()

@chat_router.post("/api/chat")
def chat(body: ChatRequest):
    try:
        question = body.question
        session_id = body.session_id
        response = ask_llm(question, session_id)
        return {"answer": response["answer"], "session_id": session_id}
    except Exception as e:
        print("Chat error:", e)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")