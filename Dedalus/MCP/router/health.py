"""MCP server health tracking with cooldown-based recovery."""

from __future__ import annotations

import time
from typing import Dict, List


class HealthTracker:
    """Track unhealthy MCP servers and allow retry after cooldown."""

    def __init__(self, cooldown_seconds: int = 300):
        self._cooldown = cooldown_seconds
        self._failures: Dict[str, float] = {}  # url -> timestamp of last failure

    def mark_unhealthy(self, url: str) -> None:
        """Record a server failure."""
        self._failures[url] = time.monotonic()

    def is_healthy(self, url: str) -> bool:
        """True if no recorded failure or cooldown has expired."""
        if url not in self._failures:
            return True
        elapsed = time.monotonic() - self._failures[url]
        if elapsed >= self._cooldown:
            del self._failures[url]
            return True
        return False

    def filter_healthy(self, urls: List[str]) -> List[str]:
        """Return only healthy URLs from the list."""
        healthy = [u for u in urls if self.is_healthy(u)]
        unhealthy = [u for u in urls if not self.is_healthy(u)]
        if unhealthy:
            import sys
            print(f"  [Health filter: {len(healthy)} healthy, {len(unhealthy)} unhealthy: {', '.join(unhealthy)}]", file=sys.stderr)
        return healthy

    def clear(self, url: str) -> None:
        """Manually clear a failure record (e.g. on successful use)."""
        self._failures.pop(url, None)