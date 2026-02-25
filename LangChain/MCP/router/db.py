"""Async Postgres connection pool and registry loader.

Replaces the hardcoded MCP_REGISTRY list with a real database query.
"""

from __future__ import annotations

import os
from typing import Any

import asyncpg


_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Return (or create) the global asyncpg connection pool."""
    global _pool
    if _pool is None:
        url = os.environ["DATABASE_URL"]
        # asyncpg wants postgresql:// not postgresql+asyncpg://
        url = url.replace("postgresql+asyncpg://", "postgresql://")
        _pool = await asyncpg.create_pool(url, min_size=2, max_size=10)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

async def load_registry() -> list[dict[str, Any]]:
    """Fetch all enabled MCP servers from Postgres."""
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT url, name, category, transport, description, keywords, command, args "
        "FROM mcp_servers WHERE enabled = true ORDER BY id"
    )
    result = []
    for row in rows:
        entry: dict[str, Any] = {
            "url": row["url"],
            "name": row["name"],
            "category": row["category"],
            "transport": row["transport"],
            "description": row["description"],
            "keywords": list(row["keywords"] or []),
        }
        # Only include stdio fields if present
        if row["command"]:
            entry["command"] = row["command"]
        if row["args"]:
            entry["args"] = list(row["args"])
        result.append(entry)
    return result


# ---------------------------------------------------------------------------
# Usage metrics
# ---------------------------------------------------------------------------

async def record_tool_use(url: str) -> None:
    """Insert a tool usage event into Postgres."""
    pool = await get_pool()
    await pool.execute("INSERT INTO tool_usage (url) VALUES ($1)", url)


async def get_top_tools(n: int = 5) -> list[str]:
    """Return the top-N most frequently used tool URLs."""
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT url, COUNT(*) AS cnt FROM tool_usage "
        "GROUP BY url ORDER BY cnt DESC LIMIT $1",
        n,
    )
    return [row["url"] for row in rows]
