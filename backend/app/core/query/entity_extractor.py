"""Entity extraction service for extracting structured information from queries."""

from typing import Dict, Any, List
import json
import structlog

from app.core.llm.client import get_llm_client
from app.core.llm.prompts import PROMPT_ENTITY_EXTRACTION

logger = structlog.get_logger(__name__)


class EntityExtractor:
    """Service for extracting entities from user messages."""

    def __init__(self):
        """Initialize the entity extractor."""
        self.llm_client = get_llm_client()
        logger.info("entity_extractor_initialized")

    def extract(self, user_message: str) -> Dict[str, Any]:
        """
        Extract entities from user message.

        Args:
            user_message: User's message

        Returns:
            Dictionary with extracted entities
        """
        try:
            logger.debug("extracting_entities", message_preview=user_message[:100])

            # Call LLM with entity extraction prompt
            response = self.llm_client.chat_completion(
                messages=[
                    {"role": "system", "content": PROMPT_ENTITY_EXTRACTION},
                    {"role": "user", "content": user_message}
                ],
                model=self.llm_client.classification_model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            # Parse result
            result = json.loads(response["content"])

            entities = result.get("entities", [])

            logger.info(
                "entities_extracted",
                count=len(entities),
                types=[e.get("type") for e in entities]
            )

            return {
                "entities": entities,
                "summary": result.get("summary", ""),
                "count": len(entities)
            }

        except json.JSONDecodeError as e:
            logger.error("entity_extraction_json_parse_failed", error=str(e))
            return {"entities": [], "summary": "Failed to parse entities", "count": 0}

        except Exception as e:
            logger.error("entity_extraction_failed", error=str(e), exc_info=e)
            return {"entities": [], "summary": f"Error: {str(e)}", "count": 0}

    def extract_by_type(self, user_message: str, entity_type: str) -> List[Dict[str, Any]]:
        """
        Extract entities of a specific type.

        Args:
            user_message: User's message
            entity_type: Type of entity to extract

        Returns:
            List of entities of the specified type
        """
        result = self.extract(user_message)
        return [
            entity for entity in result["entities"]
            if entity.get("type") == entity_type
        ]


# Global instance
_entity_extractor: Optional[EntityExtractor] = None


def get_entity_extractor() -> EntityExtractor:
    """Get or create global entity extractor instance."""
    global _entity_extractor

    if _entity_extractor is None:
        _entity_extractor = EntityExtractor()

    return _entity_extractor
