"""POST /turn endpoint - the main conversation handler."""

import time

from fastapi import APIRouter

from src.orchestrator import agent, check_end_conversation
from src.session import session_store

from .models import DebugInfo, TurnRequest, TurnResponse

router = APIRouter()


@router.post("/turn", response_model=TurnResponse)
async def turn(request: TurnRequest) -> TurnResponse:
    """
    Handle a single conversation turn.

    This endpoint:
    1. Gets or creates a session
    2. Checks for end-of-conversation intents
    3. Processes the turn through the agent
    4. Returns a speakable response

    Args:
        request: TurnRequest with session_id, user_text, and metadata

    Returns:
        TurnResponse with session_id, reply_text, and debug info
    """
    start_time = time.time()

    # Get or create session
    session_id, _ = await session_store.get_or_create(request.session_id)

    # Check for end conversation
    if check_end_conversation(request.user_text):
        return TurnResponse(
            session_id=session_id,
            reply_text="Got it — ending our conversation. Talk to you later!",
            end_conversation=True,
            debug=DebugInfo(
                latency_ms=int((time.time() - start_time) * 1000),
                mode="agent",
            ),
        )

    # Process through agent
    reply_text, tool_trace, mode = await agent.process_turn(session_id, request.user_text)

    latency_ms = int((time.time() - start_time) * 1000)

    return TurnResponse(
        session_id=session_id,
        reply_text=reply_text,
        end_conversation=False,
        debug=DebugInfo(
            tool_trace=tool_trace,
            latency_ms=latency_ms,
            mode=mode,
        ),
    )
