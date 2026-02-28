"""Local query processor that works without OpenAI API."""

from typing import Dict, Any, Optional
import re
from datetime import datetime
import structlog

from app.db.local_client import local_db
from app.core.rag.local_retriever import local_rag_retriever

logger = structlog.get_logger(__name__)


class LocalQueryProcessor:
    """Process queries using local database and simple pattern matching."""

    def __init__(self):
        """Initialize the local query processor."""
        self.rag_retriever = local_rag_retriever
        logger.info("local_query_processor_initialized")

    def classify_intent(self, query: str) -> str:
        """
        Classify query intent using pattern matching.

        Args:
            query: User query text

        Returns:
            Intent classification
        """
        query_lower = query.lower()

        # Book status queries
        if any(word in query_lower for word in ['live', 'published', 'publish', 'book', 'available', 'status']):
            return "book_status"

        # Royalty queries
        if any(word in query_lower for word in ['royalty', 'payment', 'paid', 'money', 'earnings', 'revenue']):
            return "royalty_inquiry"

        # Author copy queries
        if any(word in query_lower for word in ['copy', 'copies', 'shipped', 'delivery', 'tracking', 'author copy']):
            return "author_copy"

        # General knowledge queries
        if any(word in query_lower for word in ['how', 'what', 'process', 'policy', 'guideline', 'refund', 'addon', 'premium', 'dashboard']):
            return "general_knowledge"

        # Greeting
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return "greeting"

        return "general"

    def extract_author_info(self, identity_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract author information from identity.

        Args:
            identity_info: Identity information

        Returns:
            Author data or None
        """
        try:
            if not identity_info or not identity_info.get("author_id"):
                return None

            # Get author from database
            result = local_db.table("authors").select("*").eq("id", identity_info["author_id"]).single().execute()

            if not result.data:
                logger.warning("author_not_found", author_id=identity_info["author_id"])
                return None

            return result.data

        except Exception as e:
            logger.error("author_extraction_failed", error=str(e))
            return None

    def answer_book_status(self, author_data: Dict[str, Any]) -> str:
        """Answer book status query."""
        metadata = author_data.get("metadata", {})
        books = metadata.get("books", [])

        if not books:
            return "I don't have any book information on file for you. Please contact our support team for assistance."

        responses = []
        for book in books:
            title = book.get("title", "Unknown")
            status = book.get("status", "unknown")

            if status == "live":
                pub_date = book.get("published_date", "")
                isbn = book.get("isbn", "")
                response = f"Great news! Your book \"{title}\" is live and available for purchase."
                if pub_date:
                    response += f" It was published on {pub_date}."
                if isbn:
                    response += f" ISBN: {isbn}"
                responses.append(response)

            elif status == "in_production":
                expected = book.get("expected_date", "soon")
                responses.append(f"Your book \"{title}\" is currently in production. Expected publication date: {expected}.")

            elif status == "in_editing":
                expected = book.get("expected_date", "")
                responses.append(f"Your book \"{title}\" is in the editing phase. " + (f"Expected completion: {expected}." if expected else "Our team is working on it."))

            elif status == "in_review":
                expected = book.get("expected_date", "")
                responses.append(f"Your book \"{title}\" is under review. " + (f"Review expected to complete by: {expected}." if expected else "We'll notify you once the review is complete."))

            elif status == "submitted":
                submission_date = book.get("submission_date", "")
                responses.append(f"Your book \"{title}\" has been submitted for review. " + (f"Submission date: {submission_date}. " if submission_date else "") + "Our team will review it and get back to you soon.")

        return "\n\n".join(responses) if responses else "I couldn't find specific status information for your book. Please contact our support team."

    def answer_royalty_inquiry(self, author_data: Dict[str, Any]) -> str:
        """Answer royalty payment query."""
        metadata = author_data.get("metadata", {})
        royalty = metadata.get("royalty", {})

        next_payment = royalty.get("next_payment_date", "N/A")
        amount = royalty.get("amount", "N/A")
        period = royalty.get("period", "")
        is_bestseller = royalty.get("bestseller", False)

        if next_payment == "N/A" or amount == "N/A":
            return "Your book hasn't generated royalty payments yet, or royalty information is not available at this time. Royalties are typically paid quarterly after publication. Please contact our finance team for more details."

        response = f"Your next royalty payment is scheduled for {next_payment}."
        if amount and amount != "N/A":
            response += f" Expected amount: {amount}"
        if period:
            response += f" for {period}"

        if is_bestseller:
            response += "\n\n🎉 Congratulations! Your book has bestseller status, which may result in additional bonuses."

        response += "\n\nRoyalties are calculated based on net sales and are paid quarterly. You can view detailed breakdowns in your author dashboard."

        return response

    def answer_author_copy(self, author_data: Dict[str, Any]) -> str:
        """Answer author copy query."""
        metadata = author_data.get("metadata", {})
        author_copy = metadata.get("author_copy", {})

        status = author_copy.get("status", "unknown")

        if status == "delivered":
            delivered_date = author_copy.get("delivered_date", "")
            copies = author_copy.get("copies", 1)
            return f"Your author cop{'ies' if copies > 1 else 'y'} ({copies}) {'were' if copies > 1 else 'was'} delivered on {delivered_date}. If you haven't received them, please contact our shipping department."

        elif status == "shipped":
            tracking = author_copy.get("tracking_number", "")
            shipped_date = author_copy.get("shipped_date", "")
            response = f"Your author copy has been shipped"
            if shipped_date:
                response += f" on {shipped_date}"
            if tracking:
                response += f". Tracking number: {tracking}"
            response += ". You should receive it within 5-7 business days."
            return response

        elif status == "in_transit":
            tracking = author_copy.get("tracking_number", "")
            expected = author_copy.get("expected_delivery", "")
            response = "Your author copy is currently in transit"
            if expected:
                response += f" and expected to arrive by {expected}"
            if tracking:
                response += f". Tracking number: {tracking}"
            return response

        elif status == "production":
            expected = author_copy.get("expected_date", "")
            return f"Your author copy is being prepared. " + (f"Expected ship date: {expected}." if expected else "It will be shipped shortly after your book is published.")

        elif status == "pending":
            expected = author_copy.get("expected_date", "")
            note = author_copy.get("note", "")
            response = "Your author copy is pending. "
            if expected:
                response += f"Expected ship date: {expected}."
            if note:
                response += f" Note: {note}"
            return response

        elif status in ["not_applicable", "not_yet"]:
            note = author_copy.get("note", "Author copies are provided after publication.")
            return note

        return "I don't have specific information about your author copy. Please contact our fulfillment team for assistance."

    def answer_general_knowledge(self, query: str) -> str:
        """Answer general knowledge query using RAG."""
        # Retrieve relevant chunks
        chunks = self.rag_retriever.retrieve(query, top_k=3)

        if not chunks:
            return "I don't have specific information about that in our knowledge base. Please contact our support team at support@bookleaf.com for assistance."

        # Build context
        context = self.rag_retriever.build_context(chunks, max_tokens=1000)

        # Simple response based on retrieved context
        response = "Based on our documentation:\n\n" + context

        # Add helpful note
        response += "\n\nFor more specific information or questions not covered here, please reach out to our support team."

        return response

    def process_query(
        self,
        query: str,
        identity_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user query and generate response.

        Args:
            query: User query text
            identity_info: Identity information (if available)

        Returns:
            Response dictionary with answer and metadata
        """
        logger.info("processing_query", query=query, has_identity=bool(identity_info))

        # Classify intent
        intent = self.classify_intent(query)
        logger.info("intent_classified", intent=intent)

        # Get author data if available
        author_data = None
        if identity_info:
            author_data = self.extract_author_info(identity_info)

        # Generate response based on intent
        response = ""
        confidence = 0.5

        if intent == "greeting":
            response = f"Hello{' ' + author_data.get('full_name', '') if author_data else ''}! I'm the BookLeaf AI Assistant. How can I help you today?"
            confidence = 0.95

        elif intent == "book_status":
            if author_data:
                response = self.answer_book_status(author_data)
                confidence = 0.90
            else:
                response = "I'd be happy to check your book status! To provide accurate information, I'll need to identify you. Could you please provide your name and email address?"
                confidence = 0.70

        elif intent == "royalty_inquiry":
            if author_data:
                response = self.answer_royalty_inquiry(author_data)
                confidence = 0.90
            else:
                response = "I can help you with royalty information! To access your specific payment details, please provide your name and email address."
                confidence = 0.70

        elif intent == "author_copy":
            if author_data:
                response = self.answer_author_copy(author_data)
                confidence = 0.90
            else:
                response = "I can check the status of your author copy! Please provide your name and email address so I can look up your information."
                confidence = 0.70

        elif intent == "general_knowledge":
            response = self.answer_general_knowledge(query)
            confidence = 0.85

        else:
            # General fallback
            if author_data:
                response = f"Thank you for your question, {author_data.get('full_name', '')}. "
            response += "I understand you're asking about: " + query + "\n\n"

            # Try knowledge base
            chunks = self.rag_retriever.retrieve(query, top_k=2)
            if chunks:
                context = self.rag_retriever.build_context(chunks, max_tokens=500)
                response += "Here's what I found in our documentation:\n\n" + context
                confidence = 0.75
            else:
                response += "I don't have specific information about that. Please contact our support team at support@bookleaf.com for assistance."
                confidence = 0.60

        # Determine action based on confidence
        action = "respond" if confidence >= 0.80 else "escalate"

        result = {
            "answer": response,
            "confidence": confidence,
            "intent": intent,
            "action": action,
            "metadata": {
                "has_identity": bool(author_data),
                "author_name": author_data.get("full_name") if author_data else None,
                "processing_method": "local"
            }
        }

        logger.info(
            "query_processed",
            intent=intent,
            confidence=confidence,
            action=action
        )

        return result


# Global instance
local_query_processor = LocalQueryProcessor()
