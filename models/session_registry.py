import json
import os
from .session import Session

SESSIONS_FILE = "../session_registry.json"

class SessionRegistry:
    def __init__(self):
        self.sessions = {}

    def create_session(self):
        session = Session()
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    def find_or_create(self, session_id):
        if session_id in self.sessions:
            return self.sessions[session_id]
        session = Session(session_id=session_id)
        self.sessions[session_id] = session
        return session

    def to_dict(self):
        return {
            session_id: session.to_dict()
            for session_id, session in self.sessions.items()
        }

    def save_sessions(self):
        with open(SESSIONS_FILE, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def load_sessions(self):
        if os.path.exists(SESSIONS_FILE):
            try:
                with open(SESSIONS_FILE, "r") as f:
                    data = json.load(f)
                    self.sessions = {
                        sid: Session.from_dict(sdata) for sid, sdata in data.items()
                    }
            except json.JSONDecodeError:
                print("session_registry.json is corrupt, starting fresh.")
                self.sessions = {}

session_registry = SessionRegistry()