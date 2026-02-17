"""Azure Voice Live session manager for real-time voice interaction.

Uses the `azure.ai.voicelive.aio.connect()` context manager to establish
WebSocket connections to Azure Voice Live service.
Includes local tool support via function calling.
"""

import base64
import json
import os
from typing import Callable

from azure.ai.voicelive.aio import VoiceLiveConnection, connect
from azure.ai.voicelive.models import (
    AudioInputTranscriptionOptions,
    FunctionCallOutputItem,
    Modality,
    RequestSession,
    ServerEventType,
    ServerVad,
)
from azure.core.credentials import AzureKeyCredential

from jiri.core.logging import logger
from jiri.voice.tools import TOOL_DEFINITIONS, TOOL_HANDLERS


class VoiceAgent:
    """Manages Azure Voice Live sessions with local tool support."""

    def __init__(self):
        self.endpoint = os.getenv("AZURE_VOICE_LIVE_ENDPOINT")
        self.api_key = os.getenv("AZURE_VOICE_LIVE_API_KEY")

        if not self.endpoint or not self.api_key:
            raise ValueError("AZURE_VOICE_LIVE_ENDPOINT and AZURE_VOICE_LIVE_API_KEY must be set")

        self._connection: VoiceLiveConnection | None = None
        self._on_transcript: Callable[[str, str], None] | None = None
        self._on_audio: Callable[[bytes], None] | None = None
        self._on_speech_started: Callable[[], None] | None = None
        self._pending_tool_call: dict | None = None

    async def connect(
        self,
        on_transcript: Callable[[str, str], None] | None = None,
        on_audio: Callable[[bytes], None] | None = None,
        on_speech_started: Callable[[], None] | None = None,
    ):
        """Connect to Azure Voice Live service."""
        self._on_transcript = on_transcript
        self._on_audio = on_audio
        self._on_speech_started = on_speech_started

        # Create connection using context manager factory
        credential = AzureKeyCredential(self.api_key)

        # Connect to the realtime endpoint with explicit API version
        self._connection = await connect(
            endpoint=self.endpoint,
            credential=credential,
            model="gpt-4o-realtime-preview",
            api_version="2026-01-01-preview",  # Required for MCP/transcription features
        ).__aenter__()

        # Build tool list for session - pass FunctionTool objects directly
        tool_names = [t.name for t in TOOL_DEFINITIONS]
        logger.info(f"Registering tools: {tool_names}")

        # Create a proper RequestSession object (not raw dict)
        session_config = RequestSession(
            modalities=[Modality.TEXT, Modality.AUDIO],
            instructions="""You are Jiri, a helpful voice assistant.
- Respond naturally and conversationally.
- Be concise when appropriate, but prioritize giving complete, helpful answers.
- If an answer requires more detail to be useful, provide it.
- Avoid markdown, URLs, or technical formatting.
- Use your tools when asked for time, calculations, or data lookups.

You have access to tools: get_current_time, calculate.""",
            voice="alloy",
            input_audio_format="pcm16",
            output_audio_format="pcm16",
            input_audio_transcription=AudioInputTranscriptionOptions(model="whisper-1"),
            turn_detection=ServerVad(
                type="server_vad",
                threshold=0.5,
                prefix_padding_ms=300,
                silence_duration_ms=500,
            ),
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        # Update session with our configuration including tools
        await self._connection.session.update(session=session_config)

        print(f"✓ Azure Voice Live connected with {len(TOOL_DEFINITIONS)} tools")

    async def receive_events(self):
        """Async generator to receive events from Azure Voice Live."""
        if not self._connection:
            return

        async for event in self._connection:
            event_type = event.type if hasattr(event, "type") else event.get("type", "")

            # User speech transcription (from Whisper)
            if event_type == ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED:
                transcript = (
                    event.transcript
                    if hasattr(event, "transcript")
                    else event.get("transcript", "")
                )
                if self._on_transcript and transcript:
                    self._on_transcript("user", transcript)

            # Assistant response transcript
            elif event_type == ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE:
                transcript = (
                    event.transcript
                    if hasattr(event, "transcript")
                    else event.get("transcript", "")
                )
                if self._on_transcript and transcript:
                    self._on_transcript("assistant", transcript)

            # Audio output chunk - raw bytes from Azure
            elif event_type == ServerEventType.RESPONSE_AUDIO_DELTA:
                delta = event.delta if hasattr(event, "delta") else event.get("delta", b"")
                if delta and self._on_audio:
                    # delta is already bytes from SDK, send directly
                    if isinstance(delta, bytes):
                        self._on_audio(delta)
                    else:
                        # If base64 string, decode
                        self._on_audio(base64.b64decode(delta))

            # Barge-in detection
            elif event_type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
                if self._on_speech_started:
                    self._on_speech_started()

            # Function call arguments complete - store for execution
            elif event_type == ServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE:
                self._pending_tool_call = {
                    "call_id": event.call_id
                    if hasattr(event, "call_id")
                    else event.get("call_id", ""),
                    "name": event.name if hasattr(event, "name") else event.get("name", ""),
                    "arguments": event.arguments
                    if hasattr(event, "arguments")
                    else event.get("arguments", "{}"),
                }

            # Response complete - now execute pending tool call
            elif event_type == ServerEventType.RESPONSE_DONE:
                if self._pending_tool_call:
                    await self._handle_function_call(self._pending_tool_call)
                    self._pending_tool_call = None

            yield event

    async def _handle_function_call(self, call_info: dict):
        """Handle a function call event by executing the tool and sending the result."""
        call_id = call_info.get("call_id", "")
        name = call_info.get("name", "")
        arguments_str = call_info.get("arguments", "{}")

        logger.info(f"Function call: {name}, call_id={call_id}")

        # Parse arguments
        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError:
            arguments = {}

        # Execute the handler
        handler = TOOL_HANDLERS.get(name)
        if handler:
            try:
                result = handler(arguments)
                logger.info(f"Function result: {result[:100]}...")
            except Exception as e:
                result = json.dumps({"error": str(e)})
                logger.error(f"Function error: {e}")
        else:
            result = json.dumps({"error": f"Unknown function: {name}"})
            logger.warning(f"Unknown function called: {name}")

        # Send the result back to Azure
        if self._connection:
            # Create function call output item
            output_item = FunctionCallOutputItem(call_id=call_id, output=result)
            await self._connection.conversation.item.create(item=output_item)

            # Trigger response generation to speak the result
            await self._connection.response.create()
            logger.info("Response generation triggered after function call")

    async def send_audio(self, audio_data: bytes):
        """Send PCM16 audio data to the service."""
        if self._connection:
            # Encode to base64 for the API
            audio_b64 = base64.b64encode(audio_data).decode("ascii")
            await self._connection.input_audio_buffer.append(audio=audio_b64)

    async def disconnect(self):
        """Disconnect from the service."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            print("✓ Azure Voice Live disconnected")


# Factory function for creating voice agent (lazy init)
def create_voice_agent() -> VoiceAgent:
    """Create a new VoiceAgent instance."""
    return VoiceAgent()
