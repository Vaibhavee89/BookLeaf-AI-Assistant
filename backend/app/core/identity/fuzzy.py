"""Fuzzy matching service for identity resolution."""

from typing import List, Dict, Any, Optional, Tuple
from rapidfuzz import fuzz, process
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)


class FuzzyMatcher:
    """Service for fuzzy matching of names and identifiers."""

    def __init__(self, threshold: int = None):
        """
        Initialize fuzzy matcher.

        Args:
            threshold: Minimum match score (0-100), default from config
        """
        self.threshold = threshold or settings.fuzzy_match_threshold

        logger.info("fuzzy_matcher_initialized", threshold=self.threshold)

    def match_name(
        self,
        query_name: str,
        candidate_names: List[str],
        threshold: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find matching names using fuzzy string matching.

        Args:
            query_name: Name to search for
            candidate_names: List of names to search in
            threshold: Override default threshold

        Returns:
            List of matches with scores
        """
        if not query_name or not candidate_names:
            return []

        min_threshold = threshold or self.threshold

        logger.debug(
            "fuzzy_name_matching",
            query=query_name,
            candidates_count=len(candidate_names),
            threshold=min_threshold
        )

        try:
            # Use token_sort_ratio for better handling of name variations
            # This handles: "John Smith" vs "Smith, John" or "Smith John"
            matches = process.extract(
                query_name,
                candidate_names,
                scorer=fuzz.token_sort_ratio,
                score_cutoff=min_threshold,
                limit=10  # Return top 10 matches
            )

            results = []
            for matched_name, score, index in matches:
                results.append({
                    "matched_name": matched_name,
                    "score": score,
                    "index": index,
                    "confidence": self._score_to_confidence(score),
                    "method": "token_sort_ratio"
                })

            logger.info(
                "fuzzy_name_matches_found",
                query=query_name,
                matches_found=len(results),
                best_score=results[0]["score"] if results else 0
            )

            return results

        except Exception as e:
            logger.error(
                "fuzzy_name_matching_failed",
                query=query_name,
                error=str(e),
                exc_info=e
            )
            return []

    def match_name_advanced(
        self,
        query_name: str,
        candidates: List[Dict[str, Any]],
        name_field: str = "full_name",
        threshold: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Match names with additional context from candidate records.

        Args:
            query_name: Name to search for
            candidates: List of candidate dictionaries with name_field
            name_field: Field name containing the name
            threshold: Override default threshold

        Returns:
            List of matches with scores and candidate data
        """
        if not query_name or not candidates:
            return []

        min_threshold = threshold or self.threshold

        # Extract names and preserve indices
        candidate_names = [c.get(name_field, "") for c in candidates]
        candidate_map = {name: i for i, name in enumerate(candidate_names) if name}

        logger.debug(
            "advanced_fuzzy_matching",
            query=query_name,
            candidates_count=len(candidates),
            threshold=min_threshold
        )

        try:
            # Try multiple matching algorithms
            matches_map = {}

            # Algorithm 1: Token sort ratio (handles word order)
            matches_token_sort = process.extract(
                query_name,
                candidate_names,
                scorer=fuzz.token_sort_ratio,
                score_cutoff=min_threshold,
                limit=10
            )

            for matched_name, score, _ in matches_token_sort:
                if matched_name in candidate_map:
                    idx = candidate_map[matched_name]
                    if idx not in matches_map or matches_map[idx]["token_sort_score"] < score:
                        matches_map[idx] = {
                            "candidate": candidates[idx],
                            "matched_name": matched_name,
                            "token_sort_score": score,
                            "partial_ratio_score": 0,
                            "method": "token_sort_ratio"
                        }

            # Algorithm 2: Partial ratio (handles substrings)
            matches_partial = process.extract(
                query_name,
                candidate_names,
                scorer=fuzz.partial_ratio,
                score_cutoff=min_threshold,
                limit=10
            )

            for matched_name, score, _ in matches_partial:
                if matched_name in candidate_map:
                    idx = candidate_map[matched_name]
                    if idx in matches_map:
                        matches_map[idx]["partial_ratio_score"] = score
                    else:
                        matches_map[idx] = {
                            "candidate": candidates[idx],
                            "matched_name": matched_name,
                            "token_sort_score": 0,
                            "partial_ratio_score": score,
                            "method": "partial_ratio"
                        }

            # Calculate combined scores
            results = []
            for match_data in matches_map.values():
                # Weighted average (favor token_sort)
                combined_score = (
                    match_data["token_sort_score"] * 0.7 +
                    match_data["partial_ratio_score"] * 0.3
                )

                results.append({
                    **match_data["candidate"],
                    "matched_name": match_data["matched_name"],
                    "token_sort_score": match_data["token_sort_score"],
                    "partial_ratio_score": match_data["partial_ratio_score"],
                    "combined_score": combined_score,
                    "confidence": self._score_to_confidence(combined_score),
                    "method": match_data["method"]
                })

            # Sort by combined score
            results.sort(key=lambda x: x["combined_score"], reverse=True)

            logger.info(
                "advanced_fuzzy_matches_found",
                query=query_name,
                matches_found=len(results),
                best_score=results[0]["combined_score"] if results else 0
            )

            return results

        except Exception as e:
            logger.error(
                "advanced_fuzzy_matching_failed",
                query=query_name,
                error=str(e),
                exc_info=e
            )
            return []

    def match_partial_contact(
        self,
        query_contact: str,
        candidate_contacts: List[str],
        threshold: int = 80
    ) -> List[Tuple[str, int]]:
        """
        Match partial contact information (email local parts, phone prefixes).

        Args:
            query_contact: Contact info fragment to match
            candidate_contacts: List of complete contact info
            threshold: Minimum score (default 80)

        Returns:
            List of (matched_contact, score) tuples
        """
        if not query_contact or not candidate_contacts:
            return []

        try:
            matches = process.extract(
                query_contact,
                candidate_contacts,
                scorer=fuzz.partial_ratio,
                score_cutoff=threshold,
                limit=10
            )

            results = [(matched, score) for matched, score, _ in matches]

            logger.debug(
                "partial_contact_matches",
                query=query_contact,
                matches_found=len(results)
            )

            return results

        except Exception as e:
            logger.error(
                "partial_contact_matching_failed",
                query=query_contact,
                error=str(e)
            )
            return []

    def is_similar(
        self,
        str1: str,
        str2: str,
        threshold: Optional[int] = None
    ) -> Tuple[bool, int]:
        """
        Check if two strings are similar above threshold.

        Args:
            str1: First string
            str2: Second string
            threshold: Override default threshold

        Returns:
            Tuple of (is_similar, score)
        """
        if not str1 or not str2:
            return False, 0

        min_threshold = threshold or self.threshold

        try:
            score = fuzz.token_sort_ratio(str1, str2)
            is_similar = score >= min_threshold

            logger.debug(
                "similarity_check",
                str1=str1,
                str2=str2,
                score=score,
                is_similar=is_similar
            )

            return is_similar, score

        except Exception as e:
            logger.error(
                "similarity_check_failed",
                error=str(e)
            )
            return False, 0

    def _score_to_confidence(self, score: float) -> float:
        """
        Convert fuzzy match score (0-100) to confidence (0-1).

        Applies non-linear transformation to better reflect confidence.

        Args:
            score: Fuzzy match score (0-100)

        Returns:
            Confidence value (0.0-1.0)
        """
        # Normalize to 0-1
        normalized = score / 100.0

        # Apply sigmoid-like transformation
        # Scores above 90 -> high confidence (0.8-0.9)
        # Scores 80-90 -> medium confidence (0.7-0.8)
        # Scores below 80 -> lower confidence (0.5-0.7)

        if score >= 95:
            confidence = 0.85 + (normalized - 0.95) * 2  # 0.85-0.95
        elif score >= 90:
            confidence = 0.80 + (normalized - 0.90) * 1  # 0.80-0.85
        elif score >= 85:
            confidence = 0.75 + (normalized - 0.85) * 1  # 0.75-0.80
        else:
            confidence = 0.70 + (normalized - self.threshold/100) * 0.5  # 0.70-0.75

        # Clamp to 0.5-0.9 range for fuzzy matches
        confidence = max(0.5, min(0.9, confidence))

        return confidence


# Global instance
_fuzzy_matcher: Optional[FuzzyMatcher] = None


def get_fuzzy_matcher() -> FuzzyMatcher:
    """
    Get or create global fuzzy matcher instance.

    Returns:
        FuzzyMatcher instance
    """
    global _fuzzy_matcher

    if _fuzzy_matcher is None:
        _fuzzy_matcher = FuzzyMatcher()

    return _fuzzy_matcher
