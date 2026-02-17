"""Session tool-usage metrics — JSONL logging and top-N ranking.

Tracks which MCP servers were *actually called* (not just discovered) per
session.  On startup, reads the log to determine the most popular tools
for cache preloading.
"""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import List


class UsageMetrics:
    """Append-only JSONL logger for tool usage."""

    def __init__(self, metrics_file: Path):
        self._path = metrics_file
        self._session_tools: set[str] = set()

    # ------------------------------------------------------------------
    # Session tracking
    # ------------------------------------------------------------------

    def record_tool_use(self, url: str) -> None:
        """Record that a tool was actually invoked this session."""
        self._session_tools.add(url)

    def flush_session(self) -> None:
        """Write the current session's usage to the JSONL file."""
        if not self._session_tools:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tools_used": sorted(self._session_tools),
        }
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        self._session_tools.clear()

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_top_tools(self, n: int = 5) -> List[str]:
        """Read the full log and return the top-N most frequently used tools."""
        if not self._path.exists():
            return []

        counter: Counter[str] = Counter()
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    for tool in entry.get("tools_used", []):
                        counter[tool] += 1
                except json.JSONDecodeError:
                    continue

        return [tool for tool, _ in counter.most_common(n)]