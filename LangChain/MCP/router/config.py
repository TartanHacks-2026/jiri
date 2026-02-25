"""Router configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RouterConfig:
    """All tunables for the SmartRouter."""

    # --- Models ---
    execution_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"

    # --- Semantic search ---
    similarity_threshold: float = 0.35
    relative_score_cutoff: float = 0.7

    # --- Tool cache ---
    max_cache_size: int = 10
    preload_count: int = 5

    # --- Conversation ---
    max_history_turns: int = 20
    max_steps: int = 20

    # --- Health ---
    health_cooldown_seconds: int = 300

    # --- MCP Registry (loaded from DB at runtime; kept here as a fallback) ---
    registry: List[Dict] = field(default_factory=list)

    # --- Debug ---
    debug: bool = False