"""Session management router for retrieving conversation history."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from jiri.session import session_store

router = APIRouter(prefix="/session", tags=["session"])


class SessionMessage(BaseModel):
    """Single message in conversation."""
    role: str
    content: str
    timestamp: str = ""


class SessionHistoryResponse(BaseModel):
    """Response containing session conversation history."""
    session_id: str = Field(..., description="Session UUID")
    messages: list[SessionMessage] = Field(default_factory=list)
    created_at: str = ""


@router.get("/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str) -> SessionHistoryResponse:
    """
    Retrieve conversation history for a session.
    
    This endpoint is used by the iOS app to restore context
    when deep linking from Siri.
    """
    # Check if session exists
    try:
        _, session_data = await session_store.get_or_create(session_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get history
    history = await session_store.get_history(session_id)
    
    # Convert to response format
    messages = [
        SessionMessage(role=msg["role"], content=msg["content"])
        for msg in history
    ]
    
    return SessionHistoryResponse(
        session_id=session_id,
        messages=messages,
        created_at=session_data.created_at.isoformat() if hasattr(session_data, 'created_at') else "",
    )
