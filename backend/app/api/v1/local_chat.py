"""Chat API endpoints for local mode (without OpenAI dependency)."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import structlog

from app.core.query.local_processor import local_query_processor
from app.db.local_client import local_db

logger = structlog.get_logger(__name__)

router = APIRouter()


class IdentityInfo(BaseModel):
    """Identity information for the user."""
    name: Optional[str] = Field(None, description="Full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    platform: str = Field("web_chat", description="Platform (email, whatsapp, instagram, web_chat)")


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message", min_length=1)
    identity: Optional[IdentityInfo] = Field(None, description="User identity information")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="AI assistant response")
    confidence: float = Field(..., description="Confidence score (0-1)")
    intent: str = Field(..., description="Detected intent")
    action: str = Field(..., description="Action taken (respond or escalate)")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


def find_author_by_identity(identity: IdentityInfo) -> Optional[Dict[str, Any]]:
    """Find author by identity information."""
    try:
        # Try to find by email
        if identity.email:
            result = local_db.table("identities").select("*").eq("platform", "email").execute()
            if result.data:
                for identity_record in result.data:
                    if identity_record.get("platform_identifier", "").lower() == identity.email.lower():
                        # Get author
                        author_result = local_db.table("authors").select("*").eq("id", identity_record["author_id"]).single().execute()
                        if author_result.data:
                            return {
                                "author_id": identity_record["author_id"],
                                "identity_id": identity_record["id"],
                                "author_data": author_result.data
                            }

        # Try to find by phone
        if identity.phone:
            result = local_db.table("identities").select("*").execute()
            if result.data:
                for identity_record in result.data:
                    if identity_record.get("platform") in ["phone", "whatsapp"]:
                        # Simple phone matching (just check if numbers match)
                        stored_phone = ''.join(c for c in identity_record.get("platform_identifier", "") if c.isdigit())
                        query_phone = ''.join(c for c in identity.phone if c.isdigit())
                        if stored_phone and query_phone and stored_phone == query_phone:
                            # Get author
                            author_result = local_db.table("authors").select("*").eq("id", identity_record["author_id"]).single().execute()
                            if author_result.data:
                                return {
                                    "author_id": identity_record["author_id"],
                                    "identity_id": identity_record["id"],
                                    "author_data": author_result.data
                                }

        # Try to find by name (fuzzy)
        if identity.name:
            result = local_db.table("authors").select("*").execute()
            if result.data:
                for author in result.data:
                    if author.get("full_name", "").lower() == identity.name.lower():
                        # Get identity
                        identity_result = local_db.table("identities").select("*").eq("author_id", author["id"]).execute()
                        identity_id = identity_result.data[0]["id"] if identity_result.data else None
                        return {
                            "author_id": author["id"],
                            "identity_id": identity_id,
                            "author_data": author
                        }

        return None

    except Exception as e:
        logger.error("identity_lookup_failed", error=str(e))
        return None


@router.post("/chat/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a chat message and get AI response.

    This endpoint processes user queries using local database and knowledge base.
    No OpenAI API required.
    """
    try:
        logger.info("chat_message_received", message=request.message, has_identity=bool(request.identity))

        # Find author identity if provided
        identity_info = None
        if request.identity:
            identity_info = find_author_by_identity(request.identity)

        # Process query
        result = local_query_processor.process_query(
            query=request.message,
            identity_info=identity_info
        )

        # Create or update conversation
        conversation_id = request.conversation_id
        if not conversation_id and identity_info:
            # Create new conversation
            conv_result = local_db.table("conversations").insert({
                "author_id": identity_info["author_id"],
                "identity_id": identity_info["identity_id"],
                "platform": request.identity.platform if request.identity else "web_chat",
                "status": "active",
                "metadata": {}
            }).execute()

            if conv_result.data:
                conversation_id = conv_result.data[0]["id"]

        # Store messages if we have a conversation
        if conversation_id:
            # Store user message
            local_db.table("messages").insert({
                "conversation_id": conversation_id,
                "role": "user",
                "content": request.message,
                "confidence_score": None,
                "intent": result.get("intent"),
                "metadata": {}
            }).execute()

            # Store assistant message
            local_db.table("messages").insert({
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": result["answer"],
                "confidence_score": result["confidence"],
                "intent": result.get("intent"),
                "metadata": result.get("metadata", {})
            }).execute()

        # Create escalation if needed
        if result["action"] == "escalate" and conversation_id:
            local_db.table("escalations").insert({
                "conversation_id": conversation_id,
                "reason": f"Low confidence ({result['confidence']:.2f}) on intent: {result['intent']}",
                "status": "pending",
                "priority": "medium",
                "metadata": {
                    "query": request.message,
                    "confidence": result["confidence"]
                }
            }).execute()

        return ChatResponse(
            response=result["answer"],
            confidence=result["confidence"],
            intent=result["intent"],
            action=result["action"],
            conversation_id=conversation_id,
            metadata=result.get("metadata", {})
        )

    except Exception as e:
        logger.error("chat_message_failed", error=str(e), exc_info=e)
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.get("/chat/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    try:
        # Get conversation
        conv_result = local_db.table("conversations").select("*").eq("id", conversation_id).single().execute()

        if not conv_result.data:
            raise HTTPException(status_code=404, detail="Conversation not found")

        conversation = conv_result.data

        # Get messages
        messages_result = local_db.table("messages").select("*").eq("conversation_id", conversation_id).execute()

        messages = messages_result.data if messages_result.data else []

        return {
            "conversation": conversation,
            "messages": messages
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_conversation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        result = local_db.table("authors").select("id").execute()

        return {
            "status": "healthy",
            "mode": "local",
            "database": "sqlite",
            "authors_count": len(result.data) if result.data else 0
        }
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e)
        }
