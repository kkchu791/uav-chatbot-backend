class LLMThread:
    def stream_response(self, question: str, session) -> None:
        raise NotImplementedError