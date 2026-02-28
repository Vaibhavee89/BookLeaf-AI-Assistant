"""Chat API endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
import structlog

from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationResponse,
    CreateConversationRequest,
    CreateConversationResponse
)
from app.core.query.processor import get_query_processor
from app.db.client import get_db, Client

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    db: Client = Depends(get_db)
):
    """
    Send a message and get AI response.

    This is the main chat endpoint that processes user messages through the full pipeline:
    1. Identity resolution
    2. Intent classification
    3. RAG retrieval or database query
    4. Response generation
    5. Confidence scoring
    6. Automatic escalation if needed
    """
    logger.info(
        "chat_message_received",
        has_name=bool(request.name),
        has_email=bool(request.email),
        platform=request.platform
    )

    try:
        # Get query processor
        processor = get_query_processor()

        # Process the query
        result = processor.process_query(
            user_message=request.message,
            name=request.name,
            email=request.email,
            phone=request.phone,
            platform=request.platform,
            conversation_id=request.conversation_id
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": result.get("error", "Query processing failed"),
                    "details": result.get("details")
                }
            )

        # Build response
        response = ChatMessageResponse(
            success=result["success"],
            response=result["response"],
            confidence=result["confidence"],
            confidence_breakdown=result["confidence_breakdown"],
            should_escalate=result["should_escalate"],
            escalation=result.get("escalation"),
            metadata=result["metadata"]
        )

        logger.info(
            "chat_message_processed",
            conversation_id=result["metadata"]["conversation_id"],
            confidence=result["confidence"],
            escalated=result["should_escalate"]
        )

        return response

    except Exception as e:
        logger.error(
            "chat_message_endpoint_error",
            error=str(e),
            exc_info=e
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/conversation/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: Client = Depends(get_db)
):
    """
    Get conversation history by ID.

    Returns the conversation details and all messages.
    """
    try:
        # Fetch conversation
        conversation_response = db.table("conversations").select(
            "*"
        ).eq("id", conversation_id).execute()

        if not conversation_response.data:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )

        conversation = conversation_response.data[0]

        # Fetch messages
        messages_response = db.table("messages").select(
            "*"
        ).eq("conversation_id", conversation_id).order("created_at").execute()

        messages = messages_response.data if messages_response.data else []

        # Build response
        response = ConversationResponse(
            id=conversation["id"],
            author_id=conversation.get("author_id"),
            platform=conversation["platform"],
            status=conversation["status"],
            started_at=conversation["started_at"],
            last_message_at=conversation["last_message_at"],
            messages=messages
        )

        logger.info(
            "conversation_retrieved",
            conversation_id=conversation_id,
            message_count=len(messages)
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("conversation_retrieval_error", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve conversation: {str(e)}"
        )


@router.post("/conversation", response_model=CreateConversationResponse)
async def create_conversation(
    request: CreateConversationRequest,
    db: Client = Depends(get_db)
):
    """
    Create a new conversation with identity resolution.

    This endpoint resolves the user's identity and creates a conversation.
    """
    try:
        # Resolve identity
        from app.services.identity_service import get_identity_service

        identity_service = get_identity_service()

        identity_result = identity_service.resolve_identity(
            name=request.name,
            email=request.email,
            phone=request.phone,
            platform=request.platform
        )

        if not identity_result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Identity resolution failed: {identity_result.get('error')}"
            )

        author = identity_result["author"]
        identity = identity_result["identity"]

        # Create conversation
        conversation_response = db.table("conversations").insert({
            "author_id": author["id"],
            "identity_id": identity["id"],
            "platform": request.platform,
            "status": "active"
        }).execute()

        if not conversation_response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create conversation"
            )

        conversation = conversation_response.data[0]

        logger.info(
            "conversation_created",
            conversation_id=conversation["id"],
            author_id=author["id"]
        )

        return CreateConversationResponse(
            conversation_id=conversation["id"],
            author_id=author["id"],
            identity_id=identity["id"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("conversation_creation_error", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create conversation: {str(e)}"
        )
