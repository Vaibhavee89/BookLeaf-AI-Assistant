"""Identity service for managing author identity resolution."""

from typing import Dict, Any, Optional
import structlog

from app.core.identity.matcher import get_identity_matcher
from app.core.identity.normalizer import IdentityNormalizer

logger = structlog.get_logger(__name__)


class IdentityService:
    """High-level service for identity management."""

    def __init__(self):
        """Initialize the identity service."""
        self.matcher = get_identity_matcher()
        self.normalizer = IdentityNormalizer()

        logger.info("identity_service_initialized")

    def resolve_identity(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        platform: str = "web_chat",
        platform_identifier: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Resolve identity from provided information.

        This is the main entry point for identity resolution in the application.

        Args:
            name: Person's name
            email: Email address
            phone: Phone number
            platform: Platform source
            platform_identifier: Platform-specific ID
            context: Conversation context for disambiguation

        Returns:
            Dictionary with:
            - author: Matched or created author record
            - identity: Identity record for this platform
            - confidence: Confidence score (0.0-1.0)
            - method: Matching method used
            - reasoning: Explanation of the match
        """
        logger.info(
            "identity_resolution_requested",
            has_name=bool(name),
            has_email=bool(email),
            has_phone=bool(phone),
            platform=platform
        )

        # Validate inputs
        if not (name or email or phone):
            logger.warning("insufficient_identity_information")
            return {
                "success": False,
                "error": "At least one of name, email, or phone must be provided"
            }

        try:
            # Call the matcher
            result = self.matcher.match_identity(
                name=name,
                email=email,
                phone=phone,
                platform=platform,
                platform_identifier=platform_identifier,
                context=context
            )

            if result.get("match_found"):
                logger.info(
                    "identity_resolved",
                    author_id=result["author"]["id"],
                    identity_id=result["identity"]["id"],
                    confidence=result["confidence"],
                    method=result["method"]
                )

                return {
                    "success": True,
                    **result
                }
            else:
                logger.error(
                    "identity_resolution_failed",
                    error=result.get("error", "Unknown error")
                )
                return {
                    "success": False,
                    "error": result.get("error", "Failed to resolve identity")
                }

        except Exception as e:
            logger.error(
                "identity_resolution_exception",
                error=str(e),
                exc_info=e
            )
            return {
                "success": False,
                "error": f"Exception during identity resolution: {str(e)}"
            }

    def extract_and_resolve(
        self,
        text: str,
        platform: str = "web_chat",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract identity information from text and resolve.

        Useful for processing free-form input like messages or emails.

        Args:
            text: Text containing identity information
            platform: Platform source
            context: Additional context

        Returns:
            Identity resolution result
        """
        logger.info("extracting_and_resolving_identity_from_text")

        try:
            # Extract identifiers from text
            extracted = self.normalizer.extract_identifiers(text)

            # Extract name (simple heuristic: look for capitalized words at start)
            name = None
            lines = text.split('\n')
            if lines:
                first_line = lines[0].strip()
                # If first line looks like a name (2-4 capitalized words)
                words = first_line.split()
                if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                    name = first_line

            # Use extracted info for resolution
            email = extracted["emails"][0] if extracted["emails"] else None
            phone = extracted["phones"][0] if extracted["phones"] else None

            return self.resolve_identity(
                name=name,
                email=email,
                phone=phone,
                platform=platform,
                platform_identifier=email or phone,
                context=context
            )

        except Exception as e:
            logger.error(
                "extract_and_resolve_failed",
                error=str(e),
                exc_info=e
            )
            return {
                "success": False,
                "error": f"Failed to extract and resolve identity: {str(e)}"
            }

    def validate_identity_info(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate identity information format.

        Args:
            name: Person's name
            email: Email address
            phone: Phone number

        Returns:
            Validation results with errors if any
        """
        errors = []
        warnings = []

        # Validate email
        if email:
            if not self.normalizer.validate_email(email):
                errors.append(f"Invalid email format: {email}")

        # Validate phone
        if phone:
            if not self.normalizer.validate_phone(phone):
                errors.append(f"Invalid phone format: {phone}")

        # Validate name
        if name:
            if len(name.strip()) < 2:
                errors.append("Name is too short")
            if not any(c.isalpha() for c in name):
                errors.append("Name must contain letters")

        # Check if at least one identifier provided
        if not (name or email or phone):
            errors.append("At least one of name, email, or phone must be provided")

        # Warnings
        if name and not (email or phone):
            warnings.append("Name only provided - matching may be less accurate")

        is_valid = len(errors) == 0

        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings
        }


# Global instance
_identity_service: Optional[IdentityService] = None


def get_identity_service() -> IdentityService:
    """
    Get or create global identity service instance.

    Returns:
        IdentityService instance
    """
    global _identity_service

    if _identity_service is None:
        _identity_service = IdentityService()

    return _identity_service
