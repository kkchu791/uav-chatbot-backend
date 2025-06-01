from services.openai_client import client
from models.session_store import SessionStore
from pathlib import Path
from fastapi.responses import StreamingResponse
from typing import Generator
import time
import os


def upload_files_to_llm(session_id):
    file_paths = [
        "new_altitudes.csv",
        "new_critical_errors.csv",
        "new_gps_fixes.csv",
        "new_mode_changes.csv",
        "new_battery_temps.csv"
    ]

    uploaded_files = [
        client.files.create(file=Path(path), purpose="assistants")
        for path in file_paths
    ]

    session_store = SessionStore()
    session = session_store.find_or_create(session_id)

    for f in uploaded_files:
        session.add_file_id(f.id)

    session_store.save_sessions()

def ask_llm(question: str, session_id: str) -> Generator[str, None, None]:
    # i need to grab the session because I want to create or find thread
    # to connection my prompt with
    session_store = SessionStore()
    session = session_store.find_or_create(session_id)

    # this either uses the old thread id or creates a new one.
    if not session.get_thread_id():
        thread = client.beta.threads.create()
        session.set_thread_id(thread.id)

    # send message with files
    message = client.beta.threads.messages.create(
        thread_id=session.get_thread_id(),
        role="user",
        content=question,
        attachments=[
            {"file_id": file_id, "tools": [{"type": "code_interpreter"}]}
            for file_id in session.get_file_ids()
        ]
    )
    
    # Trigger the assistant to run the message and give a response
    stream = client.beta.threads.runs.create(
        thread_id=session.get_thread_id(),
        assistant_id=os.getenv("OPENAI_ASSISTANT_ID"),
        tools=[{"type": "code_interpreter"}],
        stream=True
    )

    #setting up queue for streaming
    queue = session.get_queue()
    if not queue:
        raise Exception("No active SSE connection for this session")

    # pump the response back to the client
    for event in stream:
        if event.event == "thread.message.delta":
            delta = event.data.delta
            for part in delta.content:
                if part.type == "text":
                    queue.put_nowait(part.text.value.strip())
                    print("Pushing to queue:", part.text.value)
                else:
                    print(f"Skipping non-text part: {part.type}")

    queue.put_nowait("[DONE]")

    session_store.save_sessions()

    return True
