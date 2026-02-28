"""Confidence scoring system for response quality assessment."""

from typing import Dict, Any, Optional
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)


class ConfidenceScorer:
    """Service for calculating multi-factor confidence scores."""

    def __init__(self):
        """Initialize the confidence scorer."""
        # Load weights from config
        self.weights = settings.confidence_weights

        logger.info(
            "confidence_scorer_initialized",
            weights=self.weights
        )

    def calculate_confidence(
        self,
        identity_confidence: Optional[float] = None,
        intent_confidence: Optional[float] = None,
        rag_relevance: Optional[float] = None,
        llm_confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate weighted confidence score from multiple factors.

        Scoring model:
        - Identity confidence (30%): How well we identified the user
        - Intent classification confidence (20%): How clear the intent is
        - RAG retrieval relevance (25%): Quality of retrieved context
        - LLM self-assessment (25%): LLM's confidence in its response

        Args:
            identity_confidence: Identity matching confidence (0-1)
            intent_confidence: Intent classification confidence (0-1)
            rag_relevance: RAG context relevance score (0-1)
            llm_confidence: LLM self-assessed confidence (0-1)

        Returns:
            Dictionary with overall confidence, breakdown, and recommendation
        """
        logger.debug(
            "calculating_confidence",
            identity=identity_confidence,
            intent=intent_confidence,
            rag=rag_relevance,
            llm=llm_confidence
        )

        # Use default values if not provided
        identity_score = identity_confidence if identity_confidence is not None else 0.5
        intent_score = intent_confidence if intent_confidence is not None else 0.5
        rag_score = rag_relevance if rag_relevance is not None else 0.5
        llm_score = llm_confidence if llm_confidence is not None else 0.5

        # Calculate weighted average
        weighted_confidence = (
            identity_score * self.weights["identity"] +
            intent_score * self.weights["intent"] +
            rag_score * self.weights["rag"] +
            llm_score * self.weights["llm"]
        )

        # Determine action based on confidence
        threshold = settings.confidence_threshold_auto_respond

        if weighted_confidence >= threshold:
            action = "auto_respond"
            recommendation = "Confidence is high enough to respond automatically"
        else:
            action = "escalate"
            recommendation = f"Confidence ({weighted_confidence:.2f}) is below threshold ({threshold}). Escalate to human agent."

        # Build breakdown
        breakdown = {
            "overall_confidence": round(weighted_confidence, 3),
            "factors": {
                "identity": {
                    "score": round(identity_score, 3),
                    "weight": self.weights["identity"],
                    "contribution": round(identity_score * self.weights["identity"], 3)
                },
                "intent": {
                    "score": round(intent_score, 3),
                    "weight": self.weights["intent"],
                    "contribution": round(intent_score * self.weights["intent"], 3)
                },
                "rag": {
                    "score": round(rag_score, 3),
                    "weight": self.weights["rag"],
                    "contribution": round(rag_score * self.weights["rag"], 3)
                },
                "llm": {
                    "score": round(llm_score, 3),
                    "weight": self.weights["llm"],
                    "contribution": round(llm_score * self.weights["llm"], 3)
                }
            },
            "action": action,
            "recommendation": recommendation,
            "threshold": threshold
        }

        # Identify weakest factor
        factors_list = [
            ("identity", identity_score),
            ("intent", intent_score),
            ("rag", rag_score),
            ("llm", llm_score)
        ]
        weakest_factor, weakest_score = min(factors_list, key=lambda x: x[1])
        breakdown["weakest_factor"] = {
            "name": weakest_factor,
            "score": round(weakest_score, 3)
        }

        logger.info(
            "confidence_calculated",
            overall=weighted_confidence,
            action=action,
            weakest_factor=weakest_factor
        )

        return breakdown

    def explain_confidence(self, breakdown: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation of confidence score.

        Args:
            breakdown: Confidence breakdown from calculate_confidence

        Returns:
            Human-readable explanation
        """
        overall = breakdown["overall_confidence"]
        action = breakdown["action"]
        weakest = breakdown["weakest_factor"]

        explanation_parts = []

        # Overall assessment
        if overall >= 0.9:
            explanation_parts.append(f"Very high confidence ({overall:.0%})")
        elif overall >= 0.8:
            explanation_parts.append(f"High confidence ({overall:.0%})")
        elif overall >= 0.7:
            explanation_parts.append(f"Moderate confidence ({overall:.0%})")
        elif overall >= 0.6:
            explanation_parts.append(f"Low confidence ({overall:.0%})")
        else:
            explanation_parts.append(f"Very low confidence ({overall:.0%})")

        # Factor breakdown
        factors = breakdown["factors"]
        explanation_parts.append("based on:")

        factor_explanations = []
        if factors["identity"]["score"] >= 0.8:
            factor_explanations.append(f"strong identity match ({factors['identity']['score']:.0%})")
        elif factors["identity"]["score"] >= 0.6:
            factor_explanations.append(f"moderate identity match ({factors['identity']['score']:.0%})")
        else:
            factor_explanations.append(f"weak identity match ({factors['identity']['score']:.0%})")

        if factors["intent"]["score"] >= 0.8:
            factor_explanations.append(f"clear intent ({factors['intent']['score']:.0%})")
        else:
            factor_explanations.append(f"uncertain intent ({factors['intent']['score']:.0%})")

        if factors["rag"]["score"] >= 0.8:
            factor_explanations.append(f"highly relevant context ({factors['rag']['score']:.0%})")
        elif factors["rag"]["score"] >= 0.6:
            factor_explanations.append(f"moderately relevant context ({factors['rag']['score']:.0%})")
        else:
            factor_explanations.append(f"low relevance context ({factors['rag']['score']:.0%})")

        explanation_parts.append(", ".join(factor_explanations))

        # Weakest link
        if weakest["score"] < 0.6:
            factor_names = {
                "identity": "identity matching",
                "intent": "intent classification",
                "rag": "knowledge base relevance",
                "llm": "response quality"
            }
            explanation_parts.append(
                f". Weakest factor: {factor_names.get(weakest['name'], weakest['name'])} ({weakest['score']:.0%})"
            )

        # Action
        if action == "escalate":
            explanation_parts.append(". Recommend escalation to human agent.")
        else:
            explanation_parts.append(". Safe to respond automatically.")

        return " ".join(explanation_parts)

    def should_escalate(self, confidence_breakdown: Dict[str, Any]) -> bool:
        """
        Determine if query should be escalated based on confidence.

        Args:
            confidence_breakdown: Result from calculate_confidence

        Returns:
            True if should escalate, False otherwise
        """
        return confidence_breakdown["action"] == "escalate"

    def get_escalation_reason(self, confidence_breakdown: Dict[str, Any]) -> str:
        """
        Get reason for escalation based on confidence breakdown.

        Args:
            confidence_breakdown: Result from calculate_confidence

        Returns:
            Human-readable escalation reason
        """
        overall = confidence_breakdown["overall_confidence"]
        weakest = confidence_breakdown["weakest_factor"]
        threshold = confidence_breakdown["threshold"]

        reasons = []

        if overall < threshold:
            reasons.append(f"Overall confidence ({overall:.0%}) below threshold ({threshold:.0%})")

        # Check individual factors
        factors = confidence_breakdown["factors"]

        if factors["identity"]["score"] < 0.5:
            reasons.append("Unable to confidently identify user")

        if factors["intent"]["score"] < 0.6:
            reasons.append("Unclear intent or ambiguous question")

        if factors["rag"]["score"] < 0.6:
            reasons.append("No relevant knowledge base information found")

        if factors["llm"]["score"] < 0.6:
            reasons.append("LLM not confident in generated response")

        if not reasons:
            reasons.append(f"Low confidence in {weakest['name']} ({weakest['score']:.0%})")

        return ". ".join(reasons)


# Global instance
_confidence_scorer: Optional[ConfidenceScorer] = None


def get_confidence_scorer() -> ConfidenceScorer:
    """
    Get or create global confidence scorer instance.

    Returns:
        ConfidenceScorer instance
    """
    global _confidence_scorer

    if _confidence_scorer is None:
        _confidence_scorer = ConfidenceScorer()

    return _confidence_scorer
