from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = Field(alias="sessionId")

