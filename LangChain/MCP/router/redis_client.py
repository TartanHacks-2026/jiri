"""Async Redis client singleton.

A single shared connection pool used by ToolCache and any other
component that needs Redis.
"""

from __future__ import annotations

import os

import redis.asyncio as aioredis


_client: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    """Return (or create) the global async Redis client."""
    global _client
    if _client is None:
        url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        _client = aioredis.from_url(url, decode_responses=True)
    return _client


async def close_redis() -> None:
    global _client
    if _client:
        await _client.aclose()
        _client = None
