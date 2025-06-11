from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    question: str
    provider: Optional[str] = "OpenAI"

