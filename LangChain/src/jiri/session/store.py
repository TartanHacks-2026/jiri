"""Redis-backed session store for multi-laptop consistency."""

import os
import uuid
from datetime import datetime
from typing import Optional

import redis.asyncio as redis

from .models import Message, SessionData


class SessionStore:
    """Redis-backed session storage with in-memory fallback."""

    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.ttl_seconds = int(os.getenv("SESSION_TTL_SECONDS", "3600"))
        self.max_history = int(os.getenv("MAX_HISTORY_LENGTH", "20"))
        self._redis: Optional[redis.Redis] = None
        self._fallback: dict[str, SessionData] = {}

    async def connect(self):
        """Initialize Redis connection."""
        try:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
            await self._redis.ping()
        except Exception:
            self._redis = None

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()

    def _generate_id(self) -> str:
        """Generate a new session ID."""
        return str(uuid.uuid4())

    async def get_or_create(self, session_id: str) -> tuple[str, SessionData]:
        """Get existing session or create new one. Returns (session_id, session_data)."""
        if not session_id:
            session_id = self._generate_id()
            session = SessionData(session_id=session_id)
            await self._save(session)
            return session_id, session

        session = await self._load(session_id)
        if session is None:
            session = SessionData(session_id=session_id)

        session.last_seen = datetime.now()
        await self._save(session)
        return session_id, session

    async def append_message(self, session_id: str, role: str, content: str):
        """Append a message to session history."""
        _, session = await self.get_or_create(session_id)
        session.history.append(Message(role=role, content=content))

        # Trim history to max length
        if len(session.history) > self.max_history:
            session.history = session.history[-self.max_history :]

        session.last_seen = datetime.now()
        await self._save(session)

    async def get_history(self, session_id: str) -> list[dict]:
        """Get conversation history for LLM context."""
        _, session = await self.get_or_create(session_id)
        return [{"role": m.role, "content": m.content} for m in session.history]

    async def _save(self, session: SessionData):
        """Save session to Redis or fallback."""
        key = f"session:{session.session_id}"
        data = session.model_dump_json()

        if self._redis:
            await self._redis.setex(key, self.ttl_seconds, data)
        else:
            self._fallback[session.session_id] = session

    async def _load(self, session_id: str) -> Optional[SessionData]:
        """Load session from Redis or fallback."""
        key = f"session:{session_id}"

        if self._redis:
            data = await self._redis.get(key)
            if data:
                return SessionData.model_validate_json(data)
        else:
            return self._fallback.get(session_id)

        return None


# Global instance
session_store = SessionStore()
