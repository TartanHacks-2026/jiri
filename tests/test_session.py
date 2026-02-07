"""Tests for session store."""

import pytest

from src.session.models import SessionData
from src.session.store import SessionStore


@pytest.fixture
def store():
    """Create fresh session store for each test."""
    return SessionStore()


class TestSessionStore:
    """Tests for SessionStore."""

    @pytest.mark.asyncio
    async def test_create_new_session(self, store):
        """Empty session_id creates new session."""
        session_id, session = await store.get_or_create("")
        assert session_id != ""
        assert isinstance(session, SessionData)
        assert session.session_id == session_id

    @pytest.mark.asyncio
    async def test_get_existing_session(self, store):
        """Existing session_id returns same session."""
        session_id, _ = await store.get_or_create("")

        # Get same session
        retrieved_id, retrieved = await store.get_or_create(session_id)
        assert retrieved_id == session_id

    @pytest.mark.asyncio
    async def test_append_message(self, store):
        """Messages are appended to history."""
        session_id, _ = await store.get_or_create("")

        await store.append_message(session_id, "user", "hello")
        await store.append_message(session_id, "assistant", "hi there")

        history = await store.get_history(session_id)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "hello"
        assert history[1]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_history_limit(self, store):
        """History is trimmed to max length."""
        store.max_history = 5
        session_id, _ = await store.get_or_create("")

        # Add more messages than max
        for i in range(10):
            await store.append_message(session_id, "user", f"message {i}")

        history = await store.get_history(session_id)
        assert len(history) <= 5
