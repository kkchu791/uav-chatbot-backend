from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest
from services.llm import ask_llm

chat_router = APIRouter()

@chat_router.post("/api/chat")
def chat(body: ChatRequest):
    try:
        question = body.question
        session_id = body.session_id
        return ask_llm(question, session_id)
    except Exception as e:
        print("Chat error:", e)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# def chat(LLMThreadFactory: thread_factory, Session: session):
#     thread = thread_factory.create()
#     conn = session.get_connection()
#     for message_chunk in thread.message("How does the knight move?"):
#         conn.send_downstream(message_chunk)


#     chat(OpenAIThreadFactory, session)