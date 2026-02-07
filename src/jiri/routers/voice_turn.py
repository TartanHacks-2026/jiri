"""Voice Turn Router.

Handles incoming voice turns from Siri Shortcuts or App Intents.
"""

import time
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from jiri.core.logging import logger
from jiri.session import session_store
from jiri.orchestrator import agent, check_end_conversation

router = APIRouter()


# Models for App Intents
class AppIntentLocation(BaseModel):
    """Location data from App Intents."""
    latitude: float
    longitude: float
    accuracy: Optional[float] = None


class DeviceContext(BaseModel):
    """Device state from App Intents."""
    battery_level: Optional[int] = None
    is_silent_mode: Optional[bool] = None
    is_dnd_enabled: Optional[bool] = None


class MetaInfo(BaseModel):
    """Client metadata passed with each request."""
    timezone: str = "America/New_York"
    device: str = "iphone"
    voice: bool = True
    app_version: Optional[str] = None
    location: Optional[AppIntentLocation] = None
    device_context: Optional[DeviceContext] = None


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
    handoff_to_app: bool = Field(default=False, description="True if app should open for visual interaction")
    deep_link_url: Optional[str] = Field(default=None, description="Deep link to open app with context")
    debug: DebugInfo = Field(default_factory=DebugInfo)


@router.post("/turn", response_model=TurnResponse)
async def turn(request: TurnRequest) -> TurnResponse:
    """
    Handle a single conversation turn.
    """
    start_time = time.time()
    
    # Log request context
    if request.meta.location:
        logger.info(f"📍 Location context: {request.meta.location}")

    # Get or create session
    session_id, _ = await session_store.get_or_create(request.session_id)

    # Check for end conversation
    if check_end_conversation(request.user_text):
        latency_ms = int((time.time() - start_time) * 1000)
        return TurnResponse(
            session_id=session_id,
            reply_text="Got it — ending our conversation. Talk to you later!",
            end_conversation=True,
            debug=DebugInfo(latency_ms=latency_ms, mode="agent"),
        )

    # Process through agent
    reply_text, tool_trace, mode = await agent.process_turn(session_id, request.user_text)

    # Check if we should handoff to app
    from jiri.orchestrator.handoff_decision import HandoffDecision
    
    should_handoff, handoff_reason = HandoffDecision.should_handoff(request.user_text)
    deep_link = None
    
    if should_handoff:
        deep_link = HandoffDecision.generate_deep_link(session_id)
        logger.info(f"🔗 Handoff triggered: {handoff_reason}")
        # Modify reply to indicate app opening
        reply_text = f"{reply_text} Opening the app for you..."

    latency_ms = int((time.time() - start_time) * 1000)

    return TurnResponse(
        session_id=session_id,
        reply_text=reply_text,
        end_conversation=False,
        handoff_to_app=should_handoff,
        deep_link_url=deep_link,
        debug=DebugInfo(
            tool_trace=tool_trace + ([handoff_reason] if should_handoff else []),
            latency_ms=latency_ms,
            mode=mode,
        ),
    )
