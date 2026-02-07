"""Demo-safe fallback responder for when agent/MCP fails."""

import re

# Keywords that trigger end of conversation
END_KEYWORDS = {"stop", "end", "goodbye", "cancel", "bye", "quit", "exit"}

# Fallback responses for common intents
FALLBACK_RESPONSES = {
    "capabilities": (
        "I can help you with three things right now: "
        "booking an Uber, checking your calendar, and answering questions. "
        "What would you like to do?"
    ),
    "uber": (
        "I found the Uber tool available. For the demo, I'll simulate a ride request. "
        "Want me to book an UberX to your usual destination?"
    ),
    "calendar": (
        "I can check your calendar. "
        "Would you like to see today's events or schedule something new?"
    ),
    "greeting": "Hey! I'm Jiri, your voice assistant. How can I help you today?",
    "thanks": "You're welcome! Anything else I can help with?",
    "default": (
        "I'm having trouble processing that right now. "
        "Could you try rephrasing, or ask me what I can do?"
    ),
}


def check_end_conversation(text: str) -> bool:
    """Check if user wants to end the conversation."""
    words = set(text.lower().split())
    return bool(words & END_KEYWORDS)


def get_fallback_response(user_text: str) -> str:
    """Get appropriate fallback response based on user input."""
    text_lower = user_text.lower()

    # Capabilities check
    if any(kw in text_lower for kw in ["what can you do", "help", "capabilities", "commands"]):
        return FALLBACK_RESPONSES["capabilities"]

    # Uber intent
    if "uber" in text_lower or "ride" in text_lower or "car" in text_lower:
        return FALLBACK_RESPONSES["uber"]

    # Calendar intent
    if "calendar" in text_lower or "schedule" in text_lower or "meeting" in text_lower:
        return FALLBACK_RESPONSES["calendar"]

    # Greetings
    if any(kw in text_lower for kw in ["hello", "hi", "hey", "good morning", "good afternoon"]):
        return FALLBACK_RESPONSES["greeting"]

    # Thanks
    if any(kw in text_lower for kw in ["thank", "thanks", "appreciate"]):
        return FALLBACK_RESPONSES["thanks"]

    return FALLBACK_RESPONSES["default"]


def format_speakable(text: str, max_sentences: int = 3) -> str:
    """Format text to be speakable (short, clean, no markdown)."""
    # Remove markdown formatting
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # Bold
    text = re.sub(r"\*(.+?)\*", r"\1", text)  # Italic
    text = re.sub(r"`(.+?)`", r"\1", text)  # Code
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)  # Links
    text = re.sub(r"#{1,6}\s*", "", text)  # Headers

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)

    # Split into sentences and limit
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) > max_sentences:
        sentences = sentences[:max_sentences]

    return " ".join(sentences)
