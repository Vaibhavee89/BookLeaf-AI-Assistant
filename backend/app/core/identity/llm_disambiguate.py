"""LLM-based identity disambiguation service."""

from typing import List, Dict, Any, Optional
import json
import openai
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)


class LLMDisambiguator:
    """Service for LLM-based identity disambiguation when fuzzy matching is inconclusive."""

    def __init__(self):
        """Initialize the LLM disambiguator."""
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.classification_model  # Use GPT-4o-mini for cost efficiency

        logger.info("llm_disambiguator_initialized", model=self.model)

    def disambiguate(
        self,
        query_identity: Dict[str, Any],
        candidate_authors: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Use LLM to disambiguate between multiple possible author matches.

        Args:
            query_identity: Dictionary with name, email, phone from query
            candidate_authors: List of potential matching authors with their info
            context: Optional conversation context

        Returns:
            Dictionary with best_match, confidence, and reasoning
        """
        if not candidate_authors:
            logger.warning("no_candidates_for_disambiguation")
            return {
                "match_found": False,
                "best_match": None,
                "confidence": 0.0,
                "reasoning": "No candidates provided"
            }

        if len(candidate_authors) == 1:
            # Only one candidate, return with medium-high confidence
            return {
                "match_found": True,
                "best_match": candidate_authors[0],
                "confidence": 0.8,
                "reasoning": "Only one candidate available"
            }

        logger.info(
            "llm_disambiguation_started",
            query_name=query_identity.get("name"),
            num_candidates=len(candidate_authors)
        )

        try:
            # Build prompt
            prompt = self._build_disambiguation_prompt(
                query_identity,
                candidate_authors,
                context
            )

            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert identity matching system. Your job is to determine which author from a list best matches the query information provided. Respond only with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistency
                response_format={"type": "json_object"}
            )

            # Parse response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            # Validate and enhance result
            final_result = self._process_llm_result(
                result,
                candidate_authors
            )

            logger.info(
                "llm_disambiguation_completed",
                match_found=final_result["match_found"],
                confidence=final_result["confidence"]
            )

            return final_result

        except json.JSONDecodeError as e:
            logger.error(
                "llm_response_json_parse_failed",
                error=str(e),
                response=result_text if 'result_text' in locals() else None
            )
            return {
                "match_found": False,
                "best_match": None,
                "confidence": 0.0,
                "reasoning": "Failed to parse LLM response"
            }

        except Exception as e:
            logger.error(
                "llm_disambiguation_failed",
                error=str(e),
                exc_info=e
            )
            return {
                "match_found": False,
                "best_match": None,
                "confidence": 0.0,
                "reasoning": f"Error during disambiguation: {str(e)}"
            }

    def _build_disambiguation_prompt(
        self,
        query_identity: Dict[str, Any],
        candidate_authors: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> str:
        """
        Build prompt for LLM disambiguation.

        Args:
            query_identity: Query information
            candidate_authors: List of candidates
            context: Optional context

        Returns:
            Formatted prompt string
        """
        # Format query identity
        query_parts = []
        if query_identity.get("name"):
            query_parts.append(f"Name: {query_identity['name']}")
        if query_identity.get("email"):
            query_parts.append(f"Email: {query_identity['email']}")
        if query_identity.get("phone"):
            query_parts.append(f"Phone: {query_identity['phone']}")

        query_info = "\n".join(query_parts)

        # Format candidates
        candidate_info = []
        for i, author in enumerate(candidate_authors, 1):
            parts = [f"Candidate {i}:"]
            parts.append(f"  - ID: {author.get('id', 'unknown')}")
            parts.append(f"  - Name: {author.get('full_name', 'N/A')}")
            parts.append(f"  - Email: {author.get('email', 'N/A')}")
            parts.append(f"  - Phone: {author.get('phone', 'N/A')}")

            # Include metadata if available
            if author.get('metadata'):
                metadata = author['metadata']
                if metadata.get('genre'):
                    parts.append(f"  - Genre: {metadata['genre']}")
                if metadata.get('books_published'):
                    parts.append(f"  - Books: {metadata['books_published']}")

            candidate_info.append("\n".join(parts))

        candidates_text = "\n\n".join(candidate_info)

        # Build full prompt
        prompt = f"""Given the following query identity information and candidate authors, determine which candidate is the best match.

QUERY IDENTITY:
{query_info}

CANDIDATE AUTHORS:
{candidates_text}
"""

        if context:
            prompt += f"\n\nCONVERSATION CONTEXT:\n{context}\n"

        prompt += """
TASK:
Analyze the query identity and candidates. Consider:
1. Name similarity (exact matches, nicknames, typos)
2. Contact information matches (email, phone)
3. Any additional context provided

Respond with a JSON object in this exact format:
{
  "match_found": true or false,
  "best_match_id": "candidate ID" or null,
  "confidence": 0.0 to 1.0,
  "reasoning": "Detailed explanation of why this is or isn't a match",
  "evidence": ["list", "of", "matching", "factors"]
}

Guidelines:
- confidence should be 0.8-0.9 for strong matches with multiple evidence points
- confidence should be 0.6-0.8 for likely matches with some evidence
- confidence should be below 0.6 for uncertain matches
- Set match_found to false if confidence is below 0.5
"""

        return prompt

    def _process_llm_result(
        self,
        llm_result: Dict[str, Any],
        candidate_authors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process and validate LLM disambiguation result.

        Args:
            llm_result: Raw LLM response
            candidate_authors: Original candidate list

        Returns:
            Processed result with full author data
        """
        # Extract fields with defaults
        match_found = llm_result.get("match_found", False)
        best_match_id = llm_result.get("best_match_id")
        confidence = float(llm_result.get("confidence", 0.0))
        reasoning = llm_result.get("reasoning", "No reasoning provided")
        evidence = llm_result.get("evidence", [])

        # Clamp confidence to 0.5-0.9 range for LLM disambiguation
        # (We don't want to give LLM matches 100% confidence)
        confidence = max(0.5, min(0.9, confidence))

        # Find matching author
        best_match = None
        if match_found and best_match_id:
            for author in candidate_authors:
                if str(author.get("id")) == str(best_match_id):
                    best_match = author
                    break

        # If match was claimed but author not found, set match_found to False
        if match_found and not best_match:
            logger.warning(
                "llm_matched_id_not_found",
                match_id=best_match_id
            )
            match_found = False
            confidence = 0.0
            reasoning += " (But matched ID not found in candidates)"

        return {
            "match_found": match_found,
            "best_match": best_match,
            "confidence": confidence,
            "reasoning": reasoning,
            "evidence": evidence,
            "method": "llm_disambiguation"
        }

    def explain_match(
        self,
        query_identity: Dict[str, Any],
        matched_author: Dict[str, Any]
    ) -> str:
        """
        Generate a human-readable explanation of why an identity was matched.

        Args:
            query_identity: Original query
            matched_author: Matched author

        Returns:
            Human-readable explanation
        """
        explanations = []

        # Name matching
        if query_identity.get("name") and matched_author.get("full_name"):
            explanations.append(
                f"Name '{query_identity['name']}' matches '{matched_author['full_name']}'"
            )

        # Email matching
        if query_identity.get("email") and matched_author.get("email"):
            if query_identity["email"].lower() == matched_author["email"].lower():
                explanations.append("Email address matches exactly")
            else:
                explanations.append("Email addresses are similar")

        # Phone matching
        if query_identity.get("phone") and matched_author.get("phone"):
            explanations.append("Phone numbers match")

        if not explanations:
            return "Match based on overall similarity of provided information"

        return ". ".join(explanations) + "."


# Global instance
_llm_disambiguator: Optional[LLMDisambiguator] = None


def get_llm_disambiguator() -> LLMDisambiguator:
    """
    Get or create global LLM disambiguator instance.

    Returns:
        LLMDisambiguator instance
    """
    global _llm_disambiguator

    if _llm_disambiguator is None:
        _llm_disambiguator = LLMDisambiguator()

    return _llm_disambiguator
