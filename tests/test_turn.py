"""Tests for POST /turn endpoint."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestTurnEndpoint:
    """Tests for /turn endpoint."""

    def test_health_check(self, client):
        """Health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_new_session_created(self, client):
        """Empty session_id creates new session."""
        response = client.post(
            "/turn",
            json={
                "session_id": "",
                "user_text": "hello",
                "client": "shortcut",
                "meta": {"voice": True},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] != ""
        assert data["reply_text"] != ""
        assert data["end_conversation"] is False

    def test_session_continuity(self, client):
        """Same session_id maintains continuity."""
        # First turn
        r1 = client.post(
            "/turn",
            json={"session_id": "", "user_text": "hello", "client": "shortcut"},
        )
        session_id = r1.json()["session_id"]

        # Second turn with same session
        r2 = client.post(
            "/turn",
            json={
                "session_id": session_id,
                "user_text": "what can you do",
                "client": "shortcut",
            },
        )
        assert r2.json()["session_id"] == session_id

    def test_end_conversation_stop(self, client):
        """'stop' keyword ends conversation."""
        response = client.post(
            "/turn",
            json={"session_id": "", "user_text": "stop", "client": "shortcut"},
        )
        assert response.json()["end_conversation"] is True

    def test_end_conversation_goodbye(self, client):
        """'goodbye' keyword ends conversation."""
        response = client.post(
            "/turn",
            json={"session_id": "", "user_text": "goodbye", "client": "shortcut"},
        )
        assert response.json()["end_conversation"] is True

    def test_reply_always_present(self, client):
        """reply_text is never empty."""
        response = client.post(
            "/turn",
            json={"session_id": "", "user_text": "random text", "client": "shortcut"},
        )
        assert response.json()["reply_text"] != ""
        assert len(response.json()["reply_text"]) > 0

    def test_debug_info_present(self, client):
        """debug field is always present."""
        response = client.post(
            "/turn",
            json={"session_id": "", "user_text": "hello", "client": "shortcut"},
        )
        data = response.json()
        assert "debug" in data
        assert "mode" in data["debug"]
        assert "latency_ms" in data["debug"]

    def test_capabilities_fallback(self, client):
        """'what can you do' triggers capabilities response."""
        response = client.post(
            "/turn",
            json={
                "session_id": "",
                "user_text": "what can you do",
                "client": "shortcut",
            },
        )
        reply = response.json()["reply_text"].lower()
        # Should mention some capability
        assert any(word in reply for word in ["help", "uber", "calendar", "can"])
