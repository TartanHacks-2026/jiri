"""Main agent orchestration logic with LLM integration."""

import os
import time
from typing import Optional

from openai import AsyncOpenAI

from src.session import session_store

from .fallback import format_speakable, get_fallback_response


class AgentOrchestrator:
    """Orchestrates conversation with LLM and tools."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self._client: Optional[AsyncOpenAI] = None

        # System prompt for voice assistant behavior
        self.system_prompt = """You are Jiri, a helpful voice assistant. Keep responses SHORT and SPEAKABLE:
- Maximum 2-3 sentences
- No markdown, URLs, or technical formatting
- Conversational and friendly tone
- If you need clarification, ask ONE simple question

You have access to tools for: booking Uber rides, checking calendars, and general knowledge.
When a tool is needed, explain what you'll do briefly."""

    async def _get_client(self) -> Optional[AsyncOpenAI]:
        """Lazily initialize OpenAI client."""
        if not self.api_key:
            return None
        if self._client is None:
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    async def process_turn(self, session_id: str, user_text: str) -> tuple[str, list[str], str]:
        """
        Process a conversation turn.

        Returns: (reply_text, tool_trace, mode)
        """
        start_time = time.time()
        tool_trace: list[str] = []

        # Get conversation history
        history = await session_store.get_history(session_id)

        # Append user message
        await session_store.append_message(session_id, "user", user_text)

        # Try LLM
        client = await self._get_client()
        if client:
            try:
                reply = await self._call_llm(client, history, user_text)
                reply = format_speakable(reply)

                # Store assistant response
                await session_store.append_message(session_id, "assistant", reply)

                return reply, tool_trace, "agent"

            except Exception as e:
                tool_trace.append(f"LLM error: {str(e)[:50]}")

        # Fallback
        reply = get_fallback_response(user_text)
        await session_store.append_message(session_id, "assistant", reply)

        return reply, tool_trace, "fallback"

    async def _call_llm(self, client: AsyncOpenAI, history: list[dict], user_text: str) -> str:
        """Call OpenAI API with conversation history."""
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add history (last 10 messages for context window efficiency)
        messages.extend(history[-10:])

        # Add current user message
        messages.append({"role": "user", "content": user_text})

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=150,  # Keep responses short for voice
            temperature=0.7,
        )

        return response.choices[0].message.content or "I didn't catch that."


# Global instance
agent = AgentOrchestrator()
