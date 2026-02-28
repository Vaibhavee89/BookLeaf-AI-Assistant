"""Intent classification service (wrapper around LLM client)."""

from typing import Dict, Any, Optional, List
import structlog

from app.core.llm.client import get_llm_client

logger = structlog.get_logger(__name__)


class IntentClassifier:
    """Service for classifying user intent."""

    def __init__(self):
        """Initialize the intent classifier."""
        self.llm_client = get_llm_client()
        logger.info("intent_classifier_initialized")

    def classify(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Classify user intent.

        This is a convenience wrapper around the LLM client's classify_intent method.

        Args:
            user_message: User's message
            conversation_history: Optional conversation history for context

        Returns:
            Dictionary with intent, confidence, and reasoning
        """
        return self.llm_client.classify_intent(
            user_message,
            conversation_history
        )


# Global instance
_intent_classifier: Optional[IntentClassifier] = None


def get_intent_classifier() -> IntentClassifier:
    """Get or create global intent classifier instance."""
    global _intent_classifier

    if _intent_classifier is None:
        _intent_classifier = IntentClassifier()

    return _intent_classifier
