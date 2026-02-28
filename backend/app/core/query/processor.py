"""Main query processor orchestrating the full conversation flow."""

from typing import Dict, Any, Optional, List
import time
import structlog

from app.core.identity.matcher import get_identity_matcher
from app.core.rag.retriever import get_vector_retriever
from app.core.rag.context_builder import get_context_builder
from app.core.llm.client import get_llm_client
from app.core.llm.prompts import (
    SYSTEM_PROMPT_BOOKLEAF_ASSISTANT,
    SYSTEM_PROMPT_RESPONSE_WITH_CONTEXT,
    build_response_prompt
)
from app.core.llm.confidence import get_confidence_scorer
from app.db.client import get_supabase_client

logger = structlog.get_logger(__name__)


class QueryProcessor:
    """
    Main orchestrator for processing user queries end-to-end.

    Flow:
    1. Resolve identity
    2. Classify intent
    3. Retrieve RAG context (for knowledge queries)
    4. Query database (for author-specific queries)
    5. Generate response with LLM
    6. Calculate confidence
    7. Route based on confidence (auto-respond or escalate)
    """

    def __init__(self):
        """Initialize the query processor."""
        self.identity_matcher = get_identity_matcher()
        self.vector_retriever = get_vector_retriever()
        self.context_builder = get_context_builder()
        self.llm_client = get_llm_client()
        self.confidence_scorer = get_confidence_scorer()
        self.supabase = get_supabase_client()

        logger.info("query_processor_initialized")

    def process_query(
        self,
        user_message: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        platform: str = "web_chat",
        conversation_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process user query end-to-end.

        Args:
            user_message: User's message/question
            name: User's name
            email: User's email
            phone: User's phone
            platform: Platform source
            conversation_id: Existing conversation ID (if continuing)
            conversation_history: Previous messages for context

        Returns:
            Dictionary with response, confidence, routing decision, and metadata
        """
        start_time = time.time()

        logger.info(
            "query_processing_started",
            message_preview=user_message[:100],
            has_name=bool(name),
            has_email=bool(email),
            platform=platform
        )

        try:
            # Step 1: Resolve Identity
            logger.debug("step_1_identity_resolution")
            identity_result = self._resolve_identity(
                name=name,
                email=email,
                phone=phone,
                platform=platform,
                context=user_message
            )

            if not identity_result["success"]:
                return self._error_response(
                    "Identity resolution failed",
                    identity_result.get("error")
                )

            author = identity_result["author"]
            identity = identity_result["identity"]
            identity_confidence = identity_result["confidence"]

            # Step 2: Classify Intent
            logger.debug("step_2_intent_classification")
            intent_result = self.llm_client.classify_intent(
                user_message,
                conversation_history
            )

            intent = intent_result.get("intent", "general_knowledge")
            intent_confidence = intent_result.get("confidence", 0.5)

            # Step 3: Retrieve Context (based on intent)
            logger.debug("step_3_context_retrieval", intent=intent)
            rag_context = None
            rag_relevance = 0.5
            author_context = None

            if intent == "general_knowledge":
                # Retrieve from knowledge base
                rag_result = self._retrieve_rag_context(user_message)
                rag_context = rag_result["context_text"]
                rag_relevance = rag_result.get("avg_relevance", 0.5)

            elif intent == "author_specific":
                # Use author's specific information
                author_context = self._get_author_context(author["id"])
                rag_relevance = 0.8  # We have specific author data

            elif intent == "technical_support":
                # Retrieve technical support knowledge
                rag_result = self._retrieve_rag_context(
                    user_message,
                    document_types=["author_dashboard", "technical_support"]
                )
                rag_context = rag_result["context_text"]
                rag_relevance = rag_result.get("avg_relevance", 0.5)

            # Step 4: Generate Response
            logger.debug("step_4_response_generation")
            response_result = self._generate_response(
                user_message=user_message,
                intent=intent,
                rag_context=rag_context,
                author_context=author_context,
                conversation_history=conversation_history
            )

            response_text = response_result["content"]
            llm_confidence = self._assess_llm_confidence(
                response_text,
                rag_context,
                intent
            )

            # Step 5: Calculate Overall Confidence
            logger.debug("step_5_confidence_calculation")
            confidence_breakdown = self.confidence_scorer.calculate_confidence(
                identity_confidence=identity_confidence,
                intent_confidence=intent_confidence,
                rag_relevance=rag_relevance,
                llm_confidence=llm_confidence
            )

            overall_confidence = confidence_breakdown["overall_confidence"]
            should_escalate = confidence_breakdown["action"] == "escalate"

            # Step 6: Create or Update Conversation
            logger.debug("step_6_conversation_management")
            if not conversation_id:
                conversation_id = self._create_conversation(
                    author_id=author["id"],
                    identity_id=identity["id"],
                    platform=platform
                )

            # Save user message
            user_message_id = self._save_message(
                conversation_id=conversation_id,
                role="user",
                content=user_message,
                intent=intent,
                confidence_score=intent_confidence
            )

            # Save assistant response
            assistant_message_id = self._save_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response_text,
                intent=intent,
                confidence_score=overall_confidence,
                confidence_breakdown=confidence_breakdown,
                rag_context=rag_context,
                llm_model=response_result["model"],
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

            # Step 7: Handle Escalation if needed
            escalation = None
            if should_escalate:
                logger.info("query_requires_escalation", confidence=overall_confidence)
                escalation = self._create_escalation(
                    conversation_id=conversation_id,
                    message_id=assistant_message_id,
                    reason=self.confidence_scorer.get_escalation_reason(confidence_breakdown),
                    confidence=overall_confidence
                )

            # Step 8: Log Analytics
            self._log_analytics(
                conversation_id=conversation_id,
                message_id=assistant_message_id,
                intent=intent,
                confidence_score=overall_confidence,
                escalated=should_escalate,
                response_time_ms=int((time.time() - start_time) * 1000),
                llm_model=response_result["model"],
                llm_tokens=response_result["usage"]["total_tokens"],
                identity_method=identity_result["method"],
                success=True
            )

            # Build final result
            result = {
                "success": True,
                "response": response_text,
                "confidence": overall_confidence,
                "confidence_breakdown": confidence_breakdown,
                "should_escalate": should_escalate,
                "escalation": escalation,
                "metadata": {
                    "conversation_id": conversation_id,
                    "author_id": author["id"],
                    "identity_id": identity["id"],
                    "identity_confidence": identity_confidence,
                    "identity_method": identity_result["method"],
                    "intent": intent,
                    "intent_confidence": intent_confidence,
                    "processing_time_ms": int((time.time() - start_time) * 1000),
                    "llm_model": response_result["model"],
                    "tokens_used": response_result["usage"]["total_tokens"]
                }
            }

            logger.info(
                "query_processing_completed",
                success=True,
                confidence=overall_confidence,
                escalated=should_escalate,
                processing_time_ms=result["metadata"]["processing_time_ms"]
            )

            return result

        except Exception as e:
            logger.error(
                "query_processing_failed",
                error=str(e),
                exc_info=e
            )

            # Log failed analytics
            self._log_analytics(
                conversation_id=conversation_id,
                message_id=None,
                intent="unknown",
                confidence_score=0.0,
                escalated=True,
                response_time_ms=int((time.time() - start_time) * 1000),
                success=False,
                error_message=str(e)
            )

            return self._error_response(
                "Query processing failed",
                str(e)
            )

    def _resolve_identity(
        self,
        name: Optional[str],
        email: Optional[str],
        phone: Optional[str],
        platform: str,
        context: str
    ) -> Dict[str, Any]:
        """Resolve user identity."""
        return self.identity_matcher.match_identity(
            name=name,
            email=email,
            phone=phone,
            platform=platform,
            context=context
        )

    def _retrieve_rag_context(
        self,
        query: str,
        document_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Retrieve and build RAG context."""
        # Retrieve relevant chunks
        chunks = self.vector_retriever.retrieve(
            query=query,
            document_types=document_types
        )

        # Build context
        context_data = self.context_builder.build_context(
            retrieved_chunks=chunks,
            query=query
        )

        # Calculate average relevance
        if chunks:
            avg_relevance = sum(c.get("similarity", 0) for c in chunks) / len(chunks)
        else:
            avg_relevance = 0.0

        return {
            **context_data,
            "avg_relevance": avg_relevance
        }

    def _get_author_context(self, author_id: str) -> Dict[str, Any]:
        """Get author-specific context from database."""
        try:
            response = self.supabase.table("authors").select("*").eq("id", author_id).execute()

            if response.data:
                return response.data[0]

            return {}

        except Exception as e:
            logger.error("author_context_fetch_failed", error=str(e))
            return {}

    def _generate_response(
        self,
        user_message: str,
        intent: str,
        rag_context: Optional[str],
        author_context: Optional[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]]
    ) -> Dict[str, Any]:
        """Generate LLM response."""
        # Choose system prompt based on context availability
        system_prompt = (
            SYSTEM_PROMPT_RESPONSE_WITH_CONTEXT
            if rag_context
            else SYSTEM_PROMPT_BOOKLEAF_ASSISTANT
        )

        # Build enhanced prompt
        prompt = build_response_prompt(
            user_message=user_message,
            rag_context=rag_context,
            author_context=author_context,
            intent=intent
        )

        return self.llm_client.generate_response(
            user_message=prompt,
            conversation_history=conversation_history,
            system_prompt=system_prompt
        )

    def _assess_llm_confidence(
        self,
        response: str,
        rag_context: Optional[str],
        intent: str
    ) -> float:
        """Assess LLM's confidence in its response."""
        # Simple heuristic-based confidence
        confidence = 0.7  # Base confidence

        # Boost if we had RAG context
        if rag_context and len(rag_context) > 100:
            confidence += 0.15

        # Adjust based on response characteristics
        if "I don't know" in response.lower() or "I'm not sure" in response.lower():
            confidence -= 0.3
        elif "contact support" in response.lower():
            confidence -= 0.2

        # Clamp to valid range
        return max(0.1, min(0.95, confidence))

    def _create_conversation(
        self,
        author_id: str,
        identity_id: str,
        platform: str
    ) -> str:
        """Create new conversation."""
        try:
            response = self.supabase.table("conversations").insert({
                "author_id": author_id,
                "identity_id": identity_id,
                "platform": platform,
                "status": "active"
            }).execute()

            if response.data:
                return response.data[0]["id"]

            logger.error("conversation_creation_failed")
            return None

        except Exception as e:
            logger.error("conversation_creation_error", error=str(e))
            return None

    def _save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
        confidence_score: Optional[float] = None,
        confidence_breakdown: Optional[Dict] = None,
        rag_context: Optional[Any] = None,
        llm_model: Optional[str] = None,
        processing_time_ms: Optional[int] = None
    ) -> Optional[str]:
        """Save message to database."""
        try:
            message_data = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "intent": intent,
                "confidence_score": confidence_score,
                "confidence_breakdown": confidence_breakdown,
                "rag_context": rag_context,
                "llm_model": llm_model,
                "processing_time_ms": processing_time_ms
            }

            response = self.supabase.table("messages").insert(message_data).execute()

            if response.data:
                return response.data[0]["id"]

            return None

        except Exception as e:
            logger.error("message_save_error", error=str(e))
            return None

    def _create_escalation(
        self,
        conversation_id: str,
        message_id: Optional[str],
        reason: str,
        confidence: float
    ) -> Dict[str, Any]:
        """Create escalation record."""
        try:
            # Determine priority based on confidence
            if confidence < 0.3:
                priority = "high"
            elif confidence < 0.5:
                priority = "medium"
            else:
                priority = "low"

            escalation_data = {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "reason": reason,
                "priority": priority,
                "status": "pending"
            }

            response = self.supabase.table("escalations").insert(escalation_data).execute()

            if response.data:
                logger.info("escalation_created", escalation_id=response.data[0]["id"])
                return response.data[0]

            return None

        except Exception as e:
            logger.error("escalation_creation_error", error=str(e))
            return None

    def _log_analytics(self, **kwargs):
        """Log query analytics."""
        try:
            self.supabase.table("query_analytics").insert(kwargs).execute()
        except Exception as e:
            logger.error("analytics_logging_failed", error=str(e))

    def _error_response(self, error: str, details: Optional[str] = None) -> Dict[str, Any]:
        """Build error response."""
        return {
            "success": False,
            "error": error,
            "details": details,
            "response": "I apologize, but I'm experiencing technical difficulties. Please try again or contact our support team.",
            "confidence": 0.0,
            "should_escalate": True
        }


# Global instance
_query_processor: Optional[QueryProcessor] = None


def get_query_processor() -> QueryProcessor:
    """
    Get or create global query processor instance.

    Returns:
        QueryProcessor instance
    """
    global _query_processor

    if _query_processor is None:
        _query_processor = QueryProcessor()

    return _query_processor
