from services.openai_client import client
from models.session_store import SessionStore
from pathlib import Path
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

def wait_for_run_completion(client, thread_id, run_id, max_retries=30, delay=1):
    for i in range(max_retries):
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print(f"[{i+1}] Run status: {run.status}")
        
        if run.status == "completed":
            return run
        elif run.status in {"failed", "cancelled", "expired"}:
            raise Exception(f"Run failed with status: {run.status} {run, 'run'}")
        
        time.sleep(delay)

    raise TimeoutError("Assistant run did not complete in time.")
    

def ask_llm(question: str, session_id: str) -> str:
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
    run = client.beta.threads.runs.create(
        thread_id=session.get_thread_id(),
        assistant_id=os.getenv("OPENAI_ASSISTANT_ID"),
        tools=[{"type": "code_interpreter"}]
    )

    # poll and wait for completion
    wait_for_run_completion(client, session.get_thread_id(), run.id)

    #fetch the latest assistant message
    messages = client.beta.threads.messages.list(thread_id=session.get_thread_id())
    answers = []
    for message in reversed(messages.data):
        if message.role == "assistant":
            for block in message.content:
                if block.type == "text":
                    answers.append(block.text.value)

    for i, text in enumerate(reversed(answers)):
        print(f"Response {i+1}: {text}")

    session_store.save_sessions()

    return {"answer": answers[-1] if answers else "No assistant response found."}
