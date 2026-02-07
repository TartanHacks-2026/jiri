"""Conversation history with sliding-window trimming."""

from __future__ import annotations

from typing import Dict, List


class ConversationHistory:
    """Maintains conversation messages with automatic trimming.

    Messages are stored as OpenAI-format dicts (``{"role": ..., "content": ...}``).
    When the turn count exceeds ``max_turns``, older turn-pairs are dropped
    from the front while keeping the conversation coherent.
    """

    def __init__(self, max_turns: int = 20):
        self._max_turns = max_turns
        self._messages: List[Dict] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, messages: List[Dict]) -> None:
        """Replace history with the messages from a RunResult, then trim."""
        self._messages = list(messages)
        self._trim()

    def get_messages(self) -> List[Dict]:
        """Return a copy of the current history."""
        return list(self._messages)

    def append_user(self, content: str) -> List[Dict]:
        """Append a user message and return the full message list for execution."""
        self._messages.append({"role": "user", "content": content})
        return list(self._messages)
    
    def rollback_last_user(self) -> None:
        """Remove the last user message (used when a turn fails completely)."""
        if not self._messages:
            return
        # Find and remove the last user message
        for i in range(len(self._messages) - 1, -1, -1):
            if self._messages[i].get("role") == "user":
                self._messages.pop(i)
                break

    @property
    def turn_count(self) -> int:
        """Count user messages as a proxy for turns."""
        return sum(1 for m in self._messages if m.get("role") == "user")

    def __len__(self) -> int:
        return len(self._messages)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _trim(self) -> None:
        """Drop oldest turn-pairs until within budget.

        Preserves system messages at the start. A 'turn' is a user message
        and everything until the next user message.
        """
        if self.turn_count <= self._max_turns:
            return

        excess = self.turn_count - self._max_turns

        # Find turn boundaries (indices of user messages)
        user_indices = [i for i, m in enumerate(self._messages) if m.get("role") == "user"]

        if len(user_indices) <= excess:
            return  # safety guard

        # Cut everything before the (excess)-th user message,
        # but keep any leading system messages.
        cut_at = user_indices[excess]
        system_prefix = []
        for m in self._messages:
            if m.get("role") == "system":
                system_prefix.append(m)
            else:
                break

        self._messages = system_prefix + self._messages[cut_at:]