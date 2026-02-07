"""Voice Chat Router.

Handles voice chat using on-device transcription + LLM + TTS.
Architecture: iOS STT (on-device) -> Text to Server -> LLM -> TTS -> Play
"""

import base64
import os
from typing import Optional

import httpx
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from pydantic import BaseModel, Field

from jiri.core.logging import logger
from jiri.session import session_store
from jiri.orchestrator import agent

router = APIRouter()

# API configuration for TTS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = "https://api.openai.com/v1"


class VoiceChatResponse(BaseModel):
    """Response from voice chat endpoint."""

    session_id: str
    transcript: str = Field(default="", description="User's transcribed speech")
    reply_text: str = Field(description="Assistant's text response")
    audio_base64: Optional[str] = Field(default=None, description="TTS audio as base64 MP3")
    error: Optional[str] = None


class TextChatRequest(BaseModel):
    """Request for text-based voice chat (on-device STT)."""

    text: str
    session_id: str = ""


async def generate_tts(text: str) -> bytes:
    """Generate TTS audio using OpenAI."""
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not configured, skipping TTS")
        return b""

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{OPENAI_BASE_URL}/audio/speech",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "tts-1",
                "input": text[:4096],  # TTS limit
                "voice": "alloy",
                "response_format": "mp3",
            },
        )

        if response.status_code != 200:
            logger.error(f"TTS API error: {response.status_code} - {response.text}")
            return b""

        return response.content


@router.post("/voice/text", response_model=VoiceChatResponse)
async def voice_text_chat(request: TextChatRequest) -> VoiceChatResponse:
    """
    Process a voice chat turn with pre-transcribed text.

    Used with on-device speech recognition (SFSpeechRecognizer on iOS).
    Much faster than server-side transcription.

    1. Receive transcribed text from iOS
    2. Get LLM response via Dedalus
    3. Generate TTS audio (optional)
    4. Return reply + audio
    """
    text = request.text.strip()
    session_id = request.session_id

    logger.info(f"Voice text chat: '{text[:50]}...', session: {session_id or 'new'}")

    if not text:
        return VoiceChatResponse(
            session_id=session_id or "",
            transcript="",
            reply_text="I didn't catch that. Could you please repeat?",
            audio_base64=None,
        )

    # Step 1: Get or create session and process through agent
    sid, _ = await session_store.get_or_create(session_id)
    reply_text, _, _ = await agent.process_turn(sid, text)
    logger.info(f"Agent reply: {reply_text[:100]}...")

    # Step 2: Generate TTS (optional, requires OPENAI_API_KEY)
    audio_base64 = None
    try:
        tts_audio = await generate_tts(reply_text)
        if tts_audio:
            audio_base64 = base64.b64encode(tts_audio).decode()
    except Exception as e:
        logger.error(f"TTS error: {e}")

    return VoiceChatResponse(
        session_id=sid,
        transcript=text,
        reply_text=reply_text,
        audio_base64=audio_base64,
    )


@router.post("/voice/chat", response_model=VoiceChatResponse)
async def voice_chat_legacy(
    audio: UploadFile = File(..., description="Audio file (deprecated, use /voice/text)"),
    session_id: str = Form(default="", description="Session ID for continuity"),
) -> VoiceChatResponse:
    """
    Legacy endpoint for audio upload.

    DEPRECATED: Use /voice/text with on-device speech recognition instead.
    This endpoint now returns an error directing to the new endpoint.
    """
    return VoiceChatResponse(
        session_id=session_id,
        transcript="",
        reply_text="Please update your app. Audio upload is deprecated. Use on-device speech recognition.",
        audio_base64=None,
        error="Use /voice/text endpoint with on-device STT",
    )
