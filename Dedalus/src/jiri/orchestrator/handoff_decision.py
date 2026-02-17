"""Handoff decision logic for Siri-to-App transitions."""

from typing import Optional


class HandoffDecision:
    """Determines when to hand off from Siri to full app."""

    # Patterns that trigger immediate handoff
    VISUAL_TRIGGERS = [
        "show me",
        "open",
        "display",
        "let me see",
        "i want to see",
        "look at",
        "view",
    ]

    # Intent keywords that require app UI
    COMPLEX_ACTIONS = [
        "book",
        "order",
        "buy",
        "purchase",
        "pay",
        "checkout",
        "form",
        "customize",
        "choose",
        "select from",
    ]

    @staticmethod
    def should_handoff(user_text: str, intent: Optional[str] = None) -> tuple[bool, str]:
        """
        Decide if conversation should transition to app.

        Args:
            user_text: User's spoken input
            intent: Optional classified intent (e.g., "book_ride", "check_calendar")

        Returns:
            (should_handoff: bool, reason: str)
        """
        text_lower = user_text.lower()

        # Check for explicit visual request
        for trigger in HandoffDecision.VISUAL_TRIGGERS:
            if trigger in text_lower:
                return True, f"Visual trigger detected: '{trigger}'"

        # Check for complex actions requiring UI
        for action in HandoffDecision.COMPLEX_ACTIONS:
            if action in text_lower:
                return True, f"Complex action requires UI: '{action}'"

        # Intent-based handoff
        if intent:
            if intent in ["book_ride", "make_purchase", "fill_form"]:
                return True, f"Intent '{intent}' requires app interaction"

        return False, "Voice-only interaction sufficient"

    @staticmethod
    def generate_deep_link(session_id: str, context: Optional[dict] = None) -> str:
        """
        Generate deep link URL for app handoff.

        Args:
            session_id: Current session UUID
            context: Optional additional context (e.g., {"view": "ride_booking"})

        Returns:
            Deep link URL string
        """
        base_url = f"jiri://continue?session_id={session_id}"

        if context:
            # Add context parameters
            for key, value in context.items():
                base_url += f"&{key}={value}"

        return base_url
