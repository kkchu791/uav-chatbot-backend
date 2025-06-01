import asyncio

class Session:
    def __init__(self, session_id=None):
        self.session_id = session_id
        self.file_ids = []
        self.thread_id = None
        self.queue = None

    def add_file_id(self, file_id):
        self.file_ids.append(file_id)

    def set_thread_id(self, thread_id):
        self.thread_id = thread_id

    def get_file_ids(self):
        return self.file_ids

    def get_thread_id(self):
        return self.thread_id
    
    def create_queue(self):
        self.queue = asyncio.Queue()

    def get_queue(self):
        return self.queue

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "file_ids": self.file_ids,
            "thread_id": self.thread_id,
        }

    def update(self, file_ids=None, thread_id=None):
        if file_ids:
            self.file_ids.extend(file_ids)
        if thread_id:
            self.thread_id = thread_id

    @classmethod
    def from_dict(cls, data):
        session = cls(session_id=data.get("session_id"))
        session.file_ids = data.get("file_ids", [])
        session.thread_id = data.get("thread_id")
        return session