import os
from .base import LLMThread
from .openai_client import client

class OpenAIThread(LLMThread):
    def __init__(self, session):
        self.session = session

    def message(self, question: str):
        # this either uses the old thread id or creates a new one.
        if not self.session.get_thread_id():
            thread = client.beta.threads.create()
            self.session.set_thread_id(thread.id)

        # build attachments
        attachments = []
        for file_id in self.session.get_file_ids():
            attachments.append({
                "file_id": file_id,
                "tools": [{"type": "code_interpreter"}]
            })
        
        message = client.beta.threads.messages.create(
            thread_id=self.session.get_thread_id(),
            role="user",
            content=question,
            attachments=attachments
        )

        print(message, 'and', attachments)

        stream = client.beta.threads.runs.create(
            thread_id=self.session.get_thread_id(),
            assistant_id=os.getenv("OPENAI_ASSISTANT_ID"),
            tools=[{"type": "code_interpreter"}],
            stream=True
        )

        print("stream", stream)

        for event in stream:
            if event.event == "thread.message.delta":
                delta = event.data.delta
                for part in delta.content:
                    if part.type == "text":
                        yield part.text.value.strip()
                    else:
                        print(f"Skipping non-text part: {part.type}")
