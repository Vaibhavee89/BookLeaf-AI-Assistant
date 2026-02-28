"""Identity normalization service for emails, phones, and names."""

import re
from typing import Optional
import phonenumbers
from phonenumbers import NumberParseException
import structlog

logger = structlog.get_logger(__name__)


class IdentityNormalizer:
    """Service for normalizing identity information."""

    @staticmethod
    def normalize_email(email: str) -> Optional[str]:
        """
        Normalize email address for matching.

        Args:
            email: Raw email address

        Returns:
            Normalized email or None if invalid
        """
        if not email or not isinstance(email, str):
            return None

        try:
            # Convert to lowercase
            email = email.lower().strip()

            # Validate basic email format
            if '@' not in email:
                logger.warning("invalid_email_format", email=email)
                return None

            # Split into local and domain parts
            local, domain = email.rsplit('@', 1)

            # Gmail-specific normalization
            if domain in ['gmail.com', 'googlemail.com']:
                # Remove dots from Gmail local part
                local = local.replace('.', '')

                # Remove plus addressing (everything after +)
                if '+' in local:
                    local = local[:local.index('+')]

                # Normalize to gmail.com
                domain = 'gmail.com'

            # Reconstruct normalized email
            normalized = f"{local}@{domain}"

            logger.debug("email_normalized", original=email, normalized=normalized)

            return normalized

        except Exception as e:
            logger.error(
                "email_normalization_failed",
                email=email,
                error=str(e)
            )
            return None

    @staticmethod
    def normalize_phone(phone: str, default_region: str = 'US') -> Optional[str]:
        """
        Normalize phone number to E.164 format.

        Args:
            phone: Raw phone number
            default_region: Default country code (ISO 3166-1 alpha-2)

        Returns:
            Normalized phone in E.164 format (+1234567890) or None if invalid
        """
        if not phone or not isinstance(phone, str):
            return None

        try:
            # Remove common formatting characters
            cleaned = re.sub(r'[^\d+]', '', phone)

            # Parse phone number
            parsed = phonenumbers.parse(cleaned, default_region)

            # Validate
            if not phonenumbers.is_valid_number(parsed):
                logger.warning("invalid_phone_number", phone=phone)
                return None

            # Convert to E.164 format
            normalized = phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164
            )

            logger.debug("phone_normalized", original=phone, normalized=normalized)

            return normalized

        except NumberParseException as e:
            logger.warning(
                "phone_parse_failed",
                phone=phone,
                error=str(e)
            )
            return None
        except Exception as e:
            logger.error(
                "phone_normalization_failed",
                phone=phone,
                error=str(e)
            )
            return None

    @staticmethod
    def normalize_name(name: str) -> Optional[str]:
        """
        Normalize person's name for matching.

        Args:
            name: Raw name

        Returns:
            Normalized name or None if invalid
        """
        if not name or not isinstance(name, str):
            return None

        try:
            # Convert to lowercase
            name = name.lower().strip()

            # Remove extra whitespace
            name = re.sub(r'\s+', ' ', name)

            # Remove common prefixes/suffixes for matching
            prefixes = ['mr', 'mrs', 'ms', 'miss', 'dr', 'prof']
            suffixes = ['jr', 'sr', 'ii', 'iii', 'iv', 'esq', 'phd', 'md']

            parts = name.split()

            # Remove prefixes
            if parts and parts[0].rstrip('.') in prefixes:
                parts = parts[1:]

            # Remove suffixes
            if parts and parts[-1].rstrip('.') in suffixes:
                parts = parts[:-1]

            normalized = ' '.join(parts)

            logger.debug("name_normalized", original=name, normalized=normalized)

            return normalized

        except Exception as e:
            logger.error(
                "name_normalization_failed",
                name=name,
                error=str(e)
            )
            return None

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email to validate

        Returns:
            True if valid, False otherwise
        """
        if not email:
            return False

        # Basic email regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str, region: str = 'US') -> bool:
        """
        Validate phone number.

        Args:
            phone: Phone number to validate
            region: Country region

        Returns:
            True if valid, False otherwise
        """
        try:
            cleaned = re.sub(r'[^\d+]', '', phone)
            parsed = phonenumbers.parse(cleaned, region)
            return phonenumbers.is_valid_number(parsed)
        except:
            return False

    @staticmethod
    def extract_identifiers(text: str) -> dict:
        """
        Extract email and phone numbers from free text.

        Args:
            text: Input text that may contain contact information

        Returns:
            Dictionary with extracted emails and phones
        """
        result = {
            "emails": [],
            "phones": []
        }

        if not text:
            return result

        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        result["emails"] = [
            IdentityNormalizer.normalize_email(email)
            for email in emails
            if IdentityNormalizer.normalize_email(email)
        ]

        # Extract phone numbers (various formats)
        phone_patterns = [
            r'\+?1?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
        ]

        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            for phone in phones:
                normalized = IdentityNormalizer.normalize_phone(phone)
                if normalized and normalized not in result["phones"]:
                    result["phones"].append(normalized)

        logger.debug(
            "identifiers_extracted",
            emails_found=len(result["emails"]),
            phones_found=len(result["phones"])
        )

        return result
