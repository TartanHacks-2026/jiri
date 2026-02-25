"""Postgres-backed tool usage metrics.

Replaces the JSONL flat file with a proper append-only Postgres table.
get_top_tools() uses a SQL GROUP BY instead of reading every line.
"""

from __future__ import annotations

from typing import List

from .db import get_pool


class UsageMetrics:
    """Postgres-backed usage tracker."""

    async def record_tool_use(self, url: str) -> None:
        """Insert a tool usage event."""
        pool = await get_pool()
        await pool.execute("INSERT INTO tool_usage (url) VALUES ($1)", url)

    async def get_top_tools(self, n: int = 5) -> List[str]:
        """Return the top-N most frequently used tool URLs."""
        pool = await get_pool()
        rows = await pool.fetch(
            "SELECT url, COUNT(*) AS cnt FROM tool_usage "
            "GROUP BY url ORDER BY cnt DESC LIMIT $1",
            n,
        )
        return [row["url"] for row in rows]