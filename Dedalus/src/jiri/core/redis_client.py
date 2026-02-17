"""Async Redis client for session state management.

Provides a high-level async Redis wrapper for:
- Voice session state (FSM: IDLE -> LISTENING -> PROCESSING -> SPEAKING)
- Tool capability caching
- Rate limiting

Follows the Zero-Trust pattern: no secrets in Redis values.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from jiri.core.config import get_settings

# Global Redis client instance
_redis_client: Redis | None = None


async def init_redis() -> None:
    """Initialize the Redis client.

    Should be called once on application startup.
    """
    global _redis_client

    settings = get_settings()
    _redis_client = redis.from_url(
        str(settings.redis_url),
        encoding="utf-8",
        decode_responses=True,
    )


async def close_redis() -> None:
    """Close the Redis client.

    Should be called on application shutdown.
    """
    global _redis_client

    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


def get_redis() -> Redis:
    """Get the Redis client instance.

    Raises:
        RuntimeError: If Redis not initialized.
    """
    if _redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis_client


class SessionState:
    """Redis-backed session state manager for voice interactions.

    Manages the FSM state for each user session:
    - IDLE: Waiting for user input
    - LISTENING: Receiving audio stream
    - PROCESSING: Executing tool / generating response
    - SPEAKING: Playing audio response
    """

    STATES = ("IDLE", "LISTENING", "PROCESSING", "SPEAKING")
    KEY_PREFIX = "session:"
    DEFAULT_TTL = 3600  # 1 hour

    def __init__(self, redis_client: Redis | None = None) -> None:
        """Initialize session state manager.

        Args:
            redis_client: Redis client instance. Uses global if None.
        """
        self._redis = redis_client

    @property
    def redis(self) -> Redis:
        """Get Redis client, using global if not provided."""
        return self._redis or get_redis()

    def _key(self, session_id: str) -> str:
        """Generate Redis key for session."""
        return f"{self.KEY_PREFIX}{session_id}"

    async def get_state(self, session_id: str) -> str:
        """Get current session state.

        Returns:
            Current state or "IDLE" if not set.
        """
        state = await self.redis.hget(self._key(session_id), "state")
        return state or "IDLE"

    async def set_state(self, session_id: str, state: str) -> None:
        """Set session state.

        Args:
            session_id: Unique session identifier.
            state: One of IDLE, LISTENING, PROCESSING, SPEAKING.

        Raises:
            ValueError: If state is invalid.
        """
        if state not in self.STATES:
            raise ValueError(f"Invalid state: {state}. Must be one of {self.STATES}")

        key = self._key(session_id)
        await self.redis.hset(key, "state", state)
        await self.redis.expire(key, self.DEFAULT_TTL)

    async def get_context(self, session_id: str) -> dict[str, Any]:
        """Get full session context.

        Returns:
            Dict with session data (state, user_id, etc).
        """
        data = await self.redis.hgetall(self._key(session_id))
        return dict(data) if data else {"state": "IDLE"}

    async def set_context(self, session_id: str, **kwargs: Any) -> None:
        """Set session context fields.

        Args:
            session_id: Unique session identifier.
            **kwargs: Key-value pairs to store.
        """
        key = self._key(session_id)
        if kwargs:
            await self.redis.hset(key, mapping={k: str(v) for k, v in kwargs.items()})
            await self.redis.expire(key, self.DEFAULT_TTL)

    async def delete(self, session_id: str) -> None:
        """Delete session data."""
        await self.redis.delete(self._key(session_id))


class ToolCache:
    """Redis cache for MCP tool capabilities.

    Caches tool manifests from Awesome-MCP to avoid repeated lookups.
    """

    KEY_PREFIX = "tool:"
    DEFAULT_TTL = 86400  # 24 hours

    def __init__(self, redis_client: Redis | None = None) -> None:
        self._redis = redis_client

    @property
    def redis(self) -> Redis:
        return self._redis or get_redis()

    async def get(self, tool_name: str) -> str | None:
        """Get cached tool manifest URL."""
        return await self.redis.get(f"{self.KEY_PREFIX}{tool_name}")

    async def set(self, tool_name: str, manifest_url: str, ttl: int | None = None) -> None:
        """Cache tool manifest URL."""
        await self.redis.set(
            f"{self.KEY_PREFIX}{tool_name}",
            manifest_url,
            ex=ttl or self.DEFAULT_TTL,
        )


@asynccontextmanager
async def redis_session() -> AsyncGenerator[Redis, None]:
    """Context manager for Redis operations.

    Usage:
        async with redis_session() as redis:
            await redis.set("key", "value")
    """
    yield get_redis()
