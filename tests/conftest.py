"""Pytest fixtures for Jiri tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from jiri.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
