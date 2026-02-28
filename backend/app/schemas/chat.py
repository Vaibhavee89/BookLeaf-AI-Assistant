"""Pydantic schemas for chat-related endpoints."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Request model for sending a chat message."""

    message: str = Field(..., min_length=1, max_length=5000, description="User's message")
    name: Optional[str] = Field(None, max_length=255, description="User's name")
    email: Optional[str] = Field(None, max_length=255, description="User's email")
    phone: Optional[str] = Field(None, max_length=50, description="User's phone number")
    platform: str = Field(default="web_chat", max_length=50, description="Platform source")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "When will my royalty payment be processed?",
                "name": "Sarah Johnson",
                "email": "sarah.johnson@email.com",
                "platform": "web_chat"
            }
        }


class ConfidenceBreakdown(BaseModel):
    """Confidence score breakdown."""

    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    action: str = Field(..., description="auto_respond or escalate")
    factors: Dict[str, Any]
    threshold: float
    weakest_factor: Dict[str, Any]


class ChatMessageResponse(BaseModel):
    """Response model for chat message."""

    success: bool
    response: str = Field(..., description="AI assistant's response")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    confidence_breakdown: ConfidenceBreakdown
    should_escalate: bool = Field(..., description="Whether query should be escalated")
    escalation: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "response": "Royalty payments are processed quarterly...",
                "confidence": 0.87,
                "should_escalate": False,
                "metadata": {
                    "conversation_id": "abc-123",
                    "intent": "general_knowledge",
                    "processing_time_ms": 1250
                }
            }
        }


class Message(BaseModel):
    """Message model for conversation history."""

    id: str
    role: str = Field(..., description="user, assistant, or system")
    content: str
    intent: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response model for conversation retrieval."""

    id: str
    author_id: Optional[str]
    platform: str
    status: str
    started_at: datetime
    last_message_at: datetime
    messages: List[Message]

    class Config:
        from_attributes = True


class CreateConversationRequest(BaseModel):
    """Request model for creating a new conversation."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    platform: str = Field(default="web_chat")


class CreateConversationResponse(BaseModel):
    """Response model for conversation creation."""

    conversation_id: str
    author_id: str
    identity_id: str
