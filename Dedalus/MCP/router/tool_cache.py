"""LRU cache for active MCP server URLs.

Keeps the most recently *used* servers connected. When capacity is exceeded,
the least-recently-used server is evicted.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import List


class ToolCache:
    """Bounded LRU cache of MCP server URLs."""

    def __init__(self, max_size: int = 10):
        self._max_size = max_size
        self._cache: OrderedDict[str, None] = OrderedDict()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, url: str) -> str | None:
        """Add a URL (or refresh it). Returns an evicted URL, if any."""
        evicted = None
        if url in self._cache:
            self._cache.move_to_end(url)
        else:
            if len(self._cache) >= self._max_size:
                evicted, _ = self._cache.popitem(last=False)  # evict oldest
            self._cache[url] = None
        return evicted

    def touch(self, url: str) -> None:
        """Mark a URL as recently used (move to end)."""
        if url in self._cache:
            self._cache.move_to_end(url)

    def evict(self, url: str) -> None:
        """Remove a specific URL from the cache."""
        self._cache.pop(url, None)

    def get_urls(self) -> List[str]:
        """Return all cached URLs (oldest first)."""
        return list(self._cache.keys())

    def preload(self, urls: List[str]) -> None:
        """Bulk-add URLs from metrics (oldest first so latest end up at tail)."""
        for url in urls:
            self.add(url)

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, url: str) -> bool:
        return url in self._cache

    def __repr__(self) -> str:
        return f"ToolCache({list(self._cache.keys())})"