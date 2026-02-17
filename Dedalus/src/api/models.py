"""Jiri API - Pydantic models for request/response schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class MetaInfo(BaseModel):
    """Client metadata passed with each request."""

    timezone: str = "America/New_York"
    device: str = "iphone"
    voice: bool = True
    app_version: Optional[str] = None


class TurnRequest(BaseModel):
    """Request body for POST /turn endpoint."""

    session_id: str = Field(default="", description="Session ID for continuity, empty for new session")
    user_text: str = Field(..., description="User's transcribed speech input")
    user_id: Optional[str] = Field(default=None, description="Optional user identifier")
    client: str = Field(default="shortcut", description="Client type: shortcut, app, web")
    meta: MetaInfo = Field(default_factory=MetaInfo)


class DebugInfo(BaseModel):
    """Debug information returned in response."""

    tool_trace: list[str] = Field(default_factory=list)
    latency_ms: int = 0
    mode: str = "agent"  # "agent" or "fallback"


class TurnResponse(BaseModel):
    """Response body for POST /turn endpoint."""

    session_id: str = Field(..., description="Session ID for next request")
    reply_text: str = Field(..., description="Agent's spoken response")
    end_conversation: bool = Field(default=False, description="True if conversation should end")
    debug: DebugInfo = Field(default_factory=DebugInfo)
