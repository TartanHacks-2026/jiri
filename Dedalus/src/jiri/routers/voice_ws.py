"""WebSocket voice streaming router for Azure Voice Live integration."""

import json
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from jiri.voice.voice_agent import create_voice_agent, VoiceAgent
from jiri.core.logging import logger


router = APIRouter(tags=["voice"])


class VoiceSession:
    """Manages a single WebSocket voice session."""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.agent: VoiceAgent | None = None
        self._running = False
        self._event_task: asyncio.Task | None = None

    async def start(self):
        """Initialize and start the voice session."""
        self._running = True

        try:
            self.agent = create_voice_agent()
            await self.agent.connect(
                on_transcript=self._on_transcript,
                on_audio=self._on_audio,
                on_speech_started=self._on_speech_started,
            )

            # Start event receiver task
            self._event_task = asyncio.create_task(self._receive_events())
            logger.info("Voice session started")

        except Exception as e:
            logger.error(f"Failed to start voice session: {e}")
            await self._send_json({"type": "error", "text": str(e)})
            raise

    async def stop(self):
        """Stop the voice session."""
        self._running = False

        if self._event_task:
            self._event_task.cancel()
            try:
                await self._event_task
            except asyncio.CancelledError:
                pass

        if self.agent:
            await self.agent.disconnect()

        logger.info("Voice session stopped")

    async def handle_audio(self, audio_data: bytes):
        """Handle incoming audio from client."""
        if self._running and self.agent:
            await self.agent.send_audio(audio_data)

    async def _receive_events(self):
        """Receive and process events from Azure Voice Live."""
        if not self.agent:
            return

        try:
            async for event in self.agent.receive_events():
                # Events are already handled via callbacks
                pass
        except Exception as e:
            logger.error(f"Event receiver error: {e}")
            await self._send_json({"type": "error", "text": str(e)})

    def _on_transcript(self, role: str, text: str):
        """Handle transcript callback - send to WebSocket."""
        asyncio.create_task(
            self._send_json(
                {
                    "type": "transcript",
                    "role": role,
                    "text": text,
                }
            )
        )

    def _on_audio(self, audio_data: bytes):
        """Handle audio output - send to WebSocket."""
        asyncio.create_task(self.websocket.send_bytes(audio_data))

    def _on_speech_started(self):
        """Handle barge-in signal."""
        asyncio.create_task(
            self._send_json(
                {
                    "type": "speech_started",
                }
            )
        )

    async def _send_json(self, data: dict):
        """Send JSON message to WebSocket."""
        try:
            await self.websocket.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")


@router.websocket("/ws")
async def voice_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time voice streaming.

    Protocol:
    - Client → Server: binary (PCM16-LE, 24kHz, mono)
    - Server → Client: binary (PCM16-LE, 24kHz, mono)
    - Server → Client: text (JSON: transcript, speech_started, call_state)
    """
    await websocket.accept()
    logger.info("WebSocket connection accepted")

    session = VoiceSession(websocket)

    try:
        await session.start()

        # Send ready signal
        await websocket.send_text(
            json.dumps(
                {
                    "type": "ready",
                    "message": "Voice session ready",
                }
            )
        )

        # Main message loop
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                break
            elif "bytes" in message:
                # Binary audio data
                await session.handle_audio(message["bytes"])
            elif "text" in message:
                # Text commands (future: could handle control messages)
                data = json.loads(message["text"])
                if data.get("type") == "end":
                    break

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected by client")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "error",
                        "text": str(e),
                    }
                )
            )
        except Exception:
            pass
    finally:
        await session.stop()
        try:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "call_state",
                        "state": "ended",
                    }
                )
            )
        except Exception:
            pass


@router.get("/voice/status")
async def voice_status():
    """Check if voice service is configured and available."""
    import os

    endpoint = os.getenv("AZURE_VOICE_LIVE_ENDPOINT")
    api_key = os.getenv("AZURE_VOICE_LIVE_API_KEY")

    return {
        "configured": bool(endpoint and api_key),
        "endpoint": endpoint[:30] + "..." if endpoint else None,
        "features": [
            "real_time_audio",
            "barge_in",
            "mcp_tools",
            "transcripts",
        ],
    }
