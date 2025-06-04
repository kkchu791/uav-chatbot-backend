class SSEConnection:
    def __init__(self, queue):
        self.queue = queue

    def send_downstream(self, chunk: str):
        self.queue.put_nowait(chunk)