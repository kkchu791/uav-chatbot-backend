from services.llm.base import LLMThread

class GroqThread(LLMThread):
    def __init__(self, session):
        self.session = session

    def message(self, question: str):
        # Placeholder: simulate streaming a response
        yield f"(Grok AI) You asked: {question}"
        yield "..."
        yield "(This is a placeholder response from GroqThread.)"