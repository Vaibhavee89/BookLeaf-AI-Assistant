"""Main identity matching pipeline orchestrator."""

from typing import Dict, Any, Optional, List, Tuple
import structlog

from app.core.identity.normalizer import IdentityNormalizer
from app.core.identity.fuzzy import get_fuzzy_matcher
from app.core.identity.llm_disambiguate import get_llm_disambiguator
from app.db.client import get_supabase_client

logger = structlog.get_logger(__name__)


class IdentityMatcher:
    """
    Multi-stage identity matching pipeline.

    Stages:
    1. Exact match on normalized identifiers (email/phone) -> 100% confidence
    2. Fuzzy match on name + partial contact -> 70-90% confidence
    3. LLM disambiguation with context -> 50-90% confidence
    4. Create new identity if confidence < 50%
    """

    def __init__(self):
        """Initialize the identity matcher."""
        self.normalizer = IdentityNormalizer()
        self.fuzzy_matcher = get_fuzzy_matcher()
        self.llm_disambiguator = get_llm_disambiguator()
        self.supabase = get_supabase_client()

        logger.info("identity_matcher_initialized")

    def match_identity(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        platform: str = "web_chat",
        platform_identifier: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Match or create identity through multi-stage pipeline.

        Args:
            name: Person's name
            email: Email address
            phone: Phone number
            platform: Platform source ('email', 'whatsapp', 'instagram', 'web_chat')
            platform_identifier: Platform-specific ID (email, phone, username, session_id)
            context: Optional conversation context for disambiguation

        Returns:
            Dictionary with matched author, identity, confidence, and method
        """
        logger.info(
            "identity_matching_started",
            name=name,
            email=email[:20] + "..." if email else None,
            phone=phone[-4:] if phone else None,
            platform=platform
        )

        # Normalize inputs
        normalized_email = self.normalizer.normalize_email(email) if email else None
        normalized_phone = self.normalizer.normalize_phone(phone) if phone else None
        normalized_name = self.normalizer.normalize_name(name) if name else None

        # Default platform identifier
        if not platform_identifier:
            platform_identifier = normalized_email or normalized_phone or f"unknown_{platform}"

        # Stage 1: Exact match on identifiers
        stage1_result = self._stage1_exact_match(
            normalized_email,
            normalized_phone,
            platform,
            platform_identifier
        )

        if stage1_result["match_found"]:
            logger.info(
                "identity_match_found_stage1",
                method="exact_match",
                confidence=stage1_result["confidence"]
            )
            return stage1_result

        # Stage 2: Fuzzy match on name + partial contact
        if normalized_name:
            stage2_result = self._stage2_fuzzy_match(
                normalized_name,
                normalized_email,
                normalized_phone,
                platform,
                platform_identifier
            )

            if stage2_result["match_found"] and stage2_result["confidence"] >= 0.75:
                logger.info(
                    "identity_match_found_stage2",
                    method="fuzzy_match",
                    confidence=stage2_result["confidence"]
                )
                return stage2_result

            # Stage 3: LLM disambiguation if fuzzy match is uncertain
            if stage2_result["match_found"] and stage2_result["confidence"] < 0.75:
                stage3_result = self._stage3_llm_disambiguation(
                    {
                        "name": name,
                        "email": email,
                        "phone": phone
                    },
                    stage2_result.get("candidates", []),
                    context
                )

                if stage3_result["match_found"]:
                    logger.info(
                        "identity_match_found_stage3",
                        method="llm_disambiguation",
                        confidence=stage3_result["confidence"]
                    )

                    # Link this new platform identity to the matched author
                    identity_created = self._create_identity_link(
                        author_id=stage3_result["author"]["id"],
                        platform=platform,
                        platform_identifier=platform_identifier,
                        confidence=stage3_result["confidence"],
                        method="llm_disambiguation"
                    )

                    return {
                        **stage3_result,
                        "identity": identity_created
                    }

        # Stage 4: Create new author and identity
        logger.info(
            "no_match_found_creating_new_identity",
            name=name,
            has_email=bool(email),
            has_phone=bool(phone)
        )

        stage4_result = self._stage4_create_new(
            name=name,
            email=email,
            phone=phone,
            platform=platform,
            platform_identifier=platform_identifier
        )

        return stage4_result

    def _stage1_exact_match(
        self,
        normalized_email: Optional[str],
        normalized_phone: Optional[str],
        platform: str,
        platform_identifier: str
    ) -> Dict[str, Any]:
        """
        Stage 1: Exact match on normalized identifiers.

        Args:
            normalized_email: Normalized email
            normalized_phone: Normalized phone
            platform: Platform source
            platform_identifier: Platform identifier

        Returns:
            Match result with 100% confidence if found
        """
        try:
            # First, check if this exact identity already exists
            query = self.supabase.table("identities").select(
                "*, authors(*)"
            ).eq("platform", platform).eq("platform_identifier", platform_identifier)

            response = query.execute()

            if response.data:
                identity = response.data[0]
                author = identity.get("authors")

                logger.debug(
                    "exact_identity_match_found",
                    identity_id=identity["id"],
                    author_id=identity["author_id"]
                )

                return {
                    "match_found": True,
                    "author": author,
                    "identity": identity,
                    "confidence": 1.0,
                    "method": "exact_identity_match",
                    "reasoning": f"Exact match on {platform} identifier"
                }

            # Check for exact match on normalized email
            if normalized_email:
                response = self.supabase.table("identities").select(
                    "*, authors(*)"
                ).eq("normalized_identifier", normalized_email).execute()

                if response.data:
                    identity = response.data[0]
                    author = identity.get("authors")

                    logger.debug(
                        "exact_email_match_found",
                        identity_id=identity["id"],
                        author_id=identity["author_id"]
                    )

                    # Create new identity link for this platform
                    new_identity = self._create_identity_link(
                        author_id=author["id"],
                        platform=platform,
                        platform_identifier=platform_identifier,
                        confidence=1.0,
                        method="exact_email_match"
                    )

                    return {
                        "match_found": True,
                        "author": author,
                        "identity": new_identity,
                        "confidence": 1.0,
                        "method": "exact_email_match",
                        "reasoning": "Exact match on normalized email address"
                    }

            # Check for exact match on normalized phone
            if normalized_phone:
                response = self.supabase.table("identities").select(
                    "*, authors(*)"
                ).eq("normalized_identifier", normalized_phone).execute()

                if response.data:
                    identity = response.data[0]
                    author = identity.get("authors")

                    logger.debug(
                        "exact_phone_match_found",
                        identity_id=identity["id"],
                        author_id=identity["author_id"]
                    )

                    # Create new identity link for this platform
                    new_identity = self._create_identity_link(
                        author_id=author["id"],
                        platform=platform,
                        platform_identifier=platform_identifier,
                        confidence=1.0,
                        method="exact_phone_match"
                    )

                    return {
                        "match_found": True,
                        "author": author,
                        "identity": new_identity,
                        "confidence": 1.0,
                        "method": "exact_phone_match",
                        "reasoning": "Exact match on normalized phone number"
                    }

            return {"match_found": False}

        except Exception as e:
            logger.error(
                "stage1_exact_match_failed",
                error=str(e),
                exc_info=e
            )
            return {"match_found": False}

    def _stage2_fuzzy_match(
        self,
        normalized_name: str,
        normalized_email: Optional[str],
        normalized_phone: Optional[str],
        platform: str,
        platform_identifier: str
    ) -> Dict[str, Any]:
        """
        Stage 2: Fuzzy match on name with contact verification.

        Args:
            normalized_name: Normalized name
            normalized_email: Normalized email
            normalized_phone: Normalized phone
            platform: Platform source
            platform_identifier: Platform identifier

        Returns:
            Match result with 70-90% confidence if found
        """
        try:
            # Get all authors for fuzzy matching
            response = self.supabase.table("authors").select("*").execute()

            if not response.data:
                return {"match_found": False}

            authors = response.data

            # Fuzzy match on names
            matches = self.fuzzy_matcher.match_name_advanced(
                normalized_name,
                authors,
                name_field="full_name",
                threshold=85
            )

            if not matches:
                return {"match_found": False}

            # Verify contact information for top matches
            verified_matches = []

            for match in matches[:5]:  # Check top 5
                author = match
                confidence = match["confidence"]

                # Boost confidence if email matches
                if normalized_email and author.get("email"):
                    author_email = self.normalizer.normalize_email(author["email"])
                    if author_email == normalized_email:
                        confidence = min(0.95, confidence + 0.15)
                        match["email_match"] = True

                # Boost confidence if phone matches
                if normalized_phone and author.get("phone"):
                    author_phone = self.normalizer.normalize_phone(author["phone"])
                    if author_phone == normalized_phone:
                        confidence = min(0.95, confidence + 0.15)
                        match["phone_match"] = True

                match["adjusted_confidence"] = confidence

                if confidence >= 0.70:
                    verified_matches.append(match)

            if not verified_matches:
                return {"match_found": False, "candidates": matches[:3]}

            # Return best match
            best_match = verified_matches[0]

            logger.debug(
                "fuzzy_match_found",
                author_id=best_match["id"],
                confidence=best_match["adjusted_confidence"]
            )

            # If confidence is high enough, create identity link
            if best_match["adjusted_confidence"] >= 0.75:
                identity = self._create_identity_link(
                    author_id=best_match["id"],
                    platform=platform,
                    platform_identifier=platform_identifier,
                    confidence=best_match["adjusted_confidence"],
                    method="fuzzy_match"
                )

                return {
                    "match_found": True,
                    "author": best_match,
                    "identity": identity,
                    "confidence": best_match["adjusted_confidence"],
                    "method": "fuzzy_match",
                    "reasoning": f"Fuzzy name match (score: {match['combined_score']:.0f})"
                }
            else:
                # Return candidates for LLM disambiguation
                return {
                    "match_found": True,
                    "confidence": best_match["adjusted_confidence"],
                    "candidates": verified_matches
                }

        except Exception as e:
            logger.error(
                "stage2_fuzzy_match_failed",
                error=str(e),
                exc_info=e
            )
            return {"match_found": False}

    def _stage3_llm_disambiguation(
        self,
        query_identity: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        context: Optional[str]
    ) -> Dict[str, Any]:
        """
        Stage 3: LLM-based disambiguation.

        Args:
            query_identity: Query information
            candidates: List of potential matches
            context: Conversation context

        Returns:
            Match result with 50-90% confidence
        """
        try:
            result = self.llm_disambiguator.disambiguate(
                query_identity,
                candidates,
                context
            )

            if result["match_found"]:
                return {
                    "match_found": True,
                    "author": result["best_match"],
                    "confidence": result["confidence"],
                    "method": "llm_disambiguation",
                    "reasoning": result["reasoning"]
                }

            return {"match_found": False}

        except Exception as e:
            logger.error(
                "stage3_llm_disambiguation_failed",
                error=str(e),
                exc_info=e
            )
            return {"match_found": False}

    def _stage4_create_new(
        self,
        name: Optional[str],
        email: Optional[str],
        phone: Optional[str],
        platform: str,
        platform_identifier: str
    ) -> Dict[str, Any]:
        """
        Stage 4: Create new author and identity.

        Args:
            name: Person's name
            email: Email address
            phone: Phone number
            platform: Platform source
            platform_identifier: Platform identifier

        Returns:
            New author and identity with appropriate confidence
        """
        try:
            # Create new author
            author_data = {
                "full_name": name or "Unknown User",
                "email": email,
                "phone": phone,
                "metadata": {
                    "created_from": platform,
                    "initial_identifier": platform_identifier
                }
            }

            author_response = self.supabase.table("authors").insert(author_data).execute()

            if not author_response.data:
                logger.error("author_creation_failed")
                return {
                    "match_found": False,
                    "error": "Failed to create new author"
                }

            new_author = author_response.data[0]

            logger.info(
                "new_author_created",
                author_id=new_author["id"],
                name=name
            )

            # Create identity
            identity = self._create_identity_link(
                author_id=new_author["id"],
                platform=platform,
                platform_identifier=platform_identifier,
                confidence=0.5,  # New identity, lower confidence
                method="new_identity_created"
            )

            return {
                "match_found": True,
                "author": new_author,
                "identity": identity,
                "confidence": 0.5,
                "method": "new_identity_created",
                "reasoning": "No existing match found, created new author profile"
            }

        except Exception as e:
            logger.error(
                "stage4_create_new_failed",
                error=str(e),
                exc_info=e
            )
            return {
                "match_found": False,
                "error": f"Failed to create new identity: {str(e)}"
            }

    def _create_identity_link(
        self,
        author_id: str,
        platform: str,
        platform_identifier: str,
        confidence: float,
        method: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new identity link for an author on a platform.

        Args:
            author_id: Author UUID
            platform: Platform name
            platform_identifier: Platform-specific identifier
            confidence: Confidence score (0-1)
            method: Matching method used

        Returns:
            Created identity record or None if failed
        """
        try:
            # Normalize identifier if possible
            normalized_identifier = None
            if '@' in platform_identifier:
                normalized_identifier = self.normalizer.normalize_email(platform_identifier)
            elif platform in ['whatsapp', 'phone']:
                normalized_identifier = self.normalizer.normalize_phone(platform_identifier)
            else:
                normalized_identifier = platform_identifier.lower().strip()

            identity_data = {
                "author_id": author_id,
                "platform": platform,
                "platform_identifier": platform_identifier,
                "normalized_identifier": normalized_identifier,
                "confidence_score": confidence,
                "matching_method": method,
                "matching_metadata": {
                    "method": method,
                    "confidence": confidence
                },
                "verified": confidence >= 0.95  # Auto-verify high confidence matches
            }

            response = self.supabase.table("identities").insert(identity_data).execute()

            if response.data:
                logger.info(
                    "identity_created",
                    identity_id=response.data[0]["id"],
                    author_id=author_id,
                    platform=platform
                )
                return response.data[0]

            return None

        except Exception as e:
            logger.error(
                "identity_creation_failed",
                author_id=author_id,
                platform=platform,
                error=str(e),
                exc_info=e
            )
            return None


# Global instance
_identity_matcher: Optional[IdentityMatcher] = None


def get_identity_matcher() -> IdentityMatcher:
    """
    Get or create global identity matcher instance.

    Returns:
        IdentityMatcher instance
    """
    global _identity_matcher

    if _identity_matcher is None:
        _identity_matcher = IdentityMatcher()

    return _identity_matcher
