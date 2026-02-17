"""Router configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class RouterConfig:
    """All tunables for the SmartRouter."""

    # --- Models ---
    execution_model: str = "gpt-4.1-mini"  # OpenAI model for agent execution
    embedding_model: str = "text-embedding-3-small"  # OpenAI model for semantic search

    # --- Semantic search ---
    similarity_threshold: float = 0.35  # Higher = more strict
    relative_score_cutoff: float = 0.7  # Higher = only return close matches

    # --- Tool cache ---
    max_cache_size: int = 10
    preload_count: int = 5

    # --- Conversation ---
    max_history_turns: int = 20
    max_steps: int = 20  # Increase to allow more tool execution steps

    # --- Health ---
    health_cooldown_seconds: int = 300  # 5 minutes

    # --- Metrics ---
    metrics_file: Path = field(default_factory=lambda: Path("data/usage_metrics.jsonl"))

    # --- MCP Registry ---
    registry: List[Dict] = field(default_factory=list)
    
    # --- Debug ---
    debug: bool = False  # Set to True to enable debug logging