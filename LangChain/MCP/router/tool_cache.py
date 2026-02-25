"""Redis-backed LRU cache for active MCP server URLs.

Replaces the in-memory OrderedDict with a Redis sorted set where
the score is the insertion/touch timestamp. Eviction removes the
lowest-scored (oldest) member when max_size is exceeded.

The Redis key is ``mcp:tool_cache``.
"""

from __future__ import annotations

import time
from typing import List

from .redis_client import get_redis

CACHE_KEY = "mcp:tool_cache"


class ToolCache:
    """Redis-backed bounded LRU cache of MCP server URLs."""

    def __init__(self, max_size: int = 10):
        self._max_size = max_size

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _redis(self):
        return get_redis()

    def _now(self) -> float:
        return time.time()

    # ------------------------------------------------------------------
    # Public API  (all async — matches the async FastAPI context)
    # ------------------------------------------------------------------

    async def add(self, url: str) -> str | None:
        """Add a URL (or refresh it). Returns an evicted URL if capacity exceeded."""
        r = self._redis()
        await r.zadd(CACHE_KEY, {url: self._now()})

        # Evict oldest if over limit
        evicted: str | None = None
        size = await r.zcard(CACHE_KEY)
        if size > self._max_size:
            # ZPOPMIN returns list of (member, score) tuples — fetch 1
            evicted_items = await r.zpopmin(CACHE_KEY, 1)
            if evicted_items:
                evicted = evicted_items[0]  # decode_responses=True → already str
        return evicted

    async def touch(self, url: str) -> None:
        """Mark a URL as recently used."""
        r = self._redis()
        # Only update score if member exists
        if await r.zscore(CACHE_KEY, url) is not None:
            await r.zadd(CACHE_KEY, {url: self._now()})

    async def evict(self, url: str) -> None:
        """Remove a specific URL from the cache."""
        await self._redis().zrem(CACHE_KEY, url)

    async def get_urls(self) -> List[str]:
        """Return all cached URLs, oldest first."""
        return await self._redis().zrange(CACHE_KEY, 0, -1)

    async def preload(self, urls: List[str]) -> None:
        """Bulk-add URLs (oldest first so latest end up with highest score)."""
        for url in urls:
            await self.add(url)

    async def __len__(self) -> int:  # type: ignore[override]
        return await self._redis().zcard(CACHE_KEY)

    async def __contains__(self, url: str) -> bool:  # type: ignore[override]
        return await self._redis().zscore(CACHE_KEY, url) is not None