"""Unit tests for identity matching system."""

import pytest
from app.core.identity.normalizer import IdentityNormalizer
from app.core.identity.fuzzy import FuzzyMatcher


class TestIdentityNormalizer:
    """Tests for IdentityNormalizer."""

    def test_normalize_email_basic(self):
        """Test basic email normalization."""
        normalizer = IdentityNormalizer()

        assert normalizer.normalize_email("Test@Example.com") == "test@example.com"
        assert normalizer.normalize_email("  user@domain.com  ") == "user@domain.com"

    def test_normalize_email_gmail(self):
        """Test Gmail-specific normalization."""
        normalizer = IdentityNormalizer()

        # Remove dots
        assert normalizer.normalize_email("john.doe@gmail.com") == "johndoe@gmail.com"

        # Remove plus addressing
        assert normalizer.normalize_email("john+test@gmail.com") == "john@gmail.com"

        # Normalize googlemail to gmail
        assert normalizer.normalize_email("john@googlemail.com") == "john@gmail.com"

    def test_normalize_phone(self):
        """Test phone normalization."""
        normalizer = IdentityNormalizer()

        # Various formats
        assert normalizer.normalize_phone("+1-555-0101") == "+15550101"
        assert normalizer.normalize_phone("(555) 123-4567") == "+15551234567"
        assert normalizer.normalize_phone("555.123.4567") == "+15551234567"

    def test_normalize_name(self):
        """Test name normalization."""
        normalizer = IdentityNormalizer()

        # Basic normalization
        assert normalizer.normalize_name("John Doe") == "john doe"
        assert normalizer.normalize_name("  Mary   Smith  ") == "mary smith"

        # Remove prefixes/suffixes
        assert normalizer.normalize_name("Mr. John Doe") == "john doe"
        assert normalizer.normalize_name("John Doe Jr.") == "john doe"
        assert normalizer.normalize_name("Dr. Jane Smith PhD") == "jane smith"

    def test_validate_email(self):
        """Test email validation."""
        normalizer = IdentityNormalizer()

        # Valid emails
        assert normalizer.validate_email("test@example.com") == True
        assert normalizer.validate_email("user.name@domain.co.uk") == True

        # Invalid emails
        assert normalizer.validate_email("invalid") == False
        assert normalizer.validate_email("@example.com") == False
        assert normalizer.validate_email("user@") == False

    def test_extract_identifiers(self):
        """Test identifier extraction from text."""
        normalizer = IdentityNormalizer()

        text = """
        My name is John Doe and my email is john.doe@example.com.
        You can also reach me at +1-555-123-4567.
        """

        result = normalizer.extract_identifiers(text)

        assert len(result["emails"]) >= 1
        assert "johndoe@example.com" in result["emails"]
        assert len(result["phones"]) >= 1


class TestFuzzyMatcher:
    """Tests for FuzzyMatcher."""

    def test_match_name_exact(self):
        """Test exact name matching."""
        matcher = FuzzyMatcher(threshold=85)

        candidates = ["John Smith", "Jane Doe", "Bob Johnson"]
        results = matcher.match_name("John Smith", candidates)

        assert len(results) > 0
        assert results[0]["matched_name"] == "John Smith"
        assert results[0]["score"] == 100

    def test_match_name_fuzzy(self):
        """Test fuzzy name matching."""
        matcher = FuzzyMatcher(threshold=85)

        candidates = ["Sarah Johnson", "John Smith", "Sarah Johnston"]
        results = matcher.match_name("Sara Johnston", candidates)

        assert len(results) > 0
        # Should match "Sarah Johnston" with high score
        assert results[0]["matched_name"] in ["Sarah Johnston", "Sarah Johnson"]
        assert results[0]["score"] >= 85

    def test_match_name_order_invariant(self):
        """Test name matching is order invariant."""
        matcher = FuzzyMatcher(threshold=85)

        candidates = ["Smith John", "Doe Jane"]
        results = matcher.match_name("John Smith", candidates)

        assert len(results) > 0
        assert results[0]["matched_name"] == "Smith John"
        assert results[0]["score"] >= 85

    def test_is_similar(self):
        """Test similarity check."""
        matcher = FuzzyMatcher(threshold=85)

        # Similar strings
        is_sim, score = matcher.is_similar("Sarah Johnson", "Sara Johnston")
        assert is_sim == True
        assert score >= 85

        # Dissimilar strings
        is_sim, score = matcher.is_similar("John Smith", "Jane Doe")
        assert is_sim == False
        assert score < 85

    def test_threshold_enforcement(self):
        """Test that threshold is enforced."""
        matcher = FuzzyMatcher(threshold=90)

        candidates = ["Sarah Johnson", "John Smith"]
        results = matcher.match_name("Sara Jon", candidates)

        # With high threshold, weak matches should be filtered
        for result in results:
            assert result["score"] >= 90


# Integration test example (requires actual database)
@pytest.mark.skip(reason="Requires database connection")
class TestIdentityMatcherIntegration:
    """Integration tests for full identity matching pipeline."""

    def test_exact_match_email(self):
        """Test exact email match retrieves correct author."""
        # This would require a test database with known data
        pass

    def test_fuzzy_match_with_contact_verification(self):
        """Test fuzzy name match with email confirmation."""
        # This would test the full pipeline
        pass

    def test_llm_disambiguation(self):
        """Test LLM disambiguation for ambiguous cases."""
        # This would test LLM disambiguation
        pass

    def test_new_identity_creation(self):
        """Test creating new identity when no match found."""
        # This would test identity creation
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
