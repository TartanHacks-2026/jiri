"""Session data models."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Message(BaseModel):
    """Single message in conversation history."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class SessionData(BaseModel):
    """Session state stored in Redis."""

    session_id: str
    history: list[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = None
    timezone: str = "America/New_York"
    device: str = "iphone"
