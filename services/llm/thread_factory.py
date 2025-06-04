from .openai_thread import OpenAIThread
from .grok_thread import GroqThread

class LLMThreadFactory:
    def create(self, provider: str, session):
        provider = provider.lower()
        if provider == "openai":
            print('get here in thread factory')
            return OpenAIThread(session)
        elif provider == "grok":
            return GroqThread(session)
        else:
            raise ValueError(f"Unknown provider: {provider}")