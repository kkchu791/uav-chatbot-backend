from services.llm.openai_thread import OpenAIThread
from services.sse.connection import SSEConnection  

def run_chat_stream(thread, question: str):
    queue = thread.session.queue
    conn = SSEConnection(queue)

    for message_chunk in thread.message(question):
        conn.send_downstream(message_chunk)
