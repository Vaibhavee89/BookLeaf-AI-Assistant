"""Data models for database entities."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


class Author(BaseModel):
    """Author model representing a BookLeaf author."""

    id: Optional[UUID] = None
    full_name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Identity(BaseModel):
    """Identity model representing a platform-specific identity."""

    id: Optional[UUID] = None
    author_id: Optional[UUID] = None
    platform: str = Field(..., max_length=50)  # 'email', 'whatsapp', 'instagram', 'web_chat'
    platform_identifier: str = Field(..., max_length=255)
    normalized_identifier: Optional[str] = Field(None, max_length=255)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    matching_method: Optional[str] = Field(None, max_length=50)  # 'exact', 'fuzzy', 'llm', 'manual'
    matching_metadata: Dict[str, Any] = Field(default_factory=dict)
    verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Conversation(BaseModel):
    """Conversation model representing a chat session."""

    id: Optional[UUID] = None
    author_id: Optional[UUID] = None
    identity_id: Optional[UUID] = None
    platform: str = Field(..., max_length=50)
    status: str = Field(default='active', max_length=50)  # 'active', 'closed', 'escalated'
    metadata: Dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Message(BaseModel):
    """Message model representing a single message in a conversation."""

    id: Optional[UUID] = None
    conversation_id: UUID
    role: str = Field(..., max_length=50)  # 'user', 'assistant', 'system'
    content: str = Field(..., min_length=1)
    intent: Optional[str] = Field(None, max_length=100)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_breakdown: Optional[Dict[str, Any]] = None
    rag_context: Optional[Dict[str, Any]] = None
    llm_model: Optional[str] = Field(None, max_length=100)
    processing_time_ms: Optional[int] = Field(None, ge=0)
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KnowledgeDocument(BaseModel):
    """Knowledge document model for RAG system."""

    id: Optional[UUID] = None
    title: str = Field(..., max_length=500)
    document_type: Optional[str] = Field(None, max_length=100)
    content: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KnowledgeEmbedding(BaseModel):
    """Knowledge embedding model for vector search."""

    id: Optional[UUID] = None
    document_id: UUID
    chunk_text: str = Field(..., min_length=1)
    chunk_index: int = Field(..., ge=0)
    embedding: Optional[List[float]] = None  # Vector embedding
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Escalation(BaseModel):
    """Escalation model for queries requiring human intervention."""

    id: Optional[UUID] = None
    conversation_id: UUID
    message_id: Optional[UUID] = None
    reason: str = Field(..., max_length=500)
    priority: str = Field(default='medium', max_length=50)  # 'low', 'medium', 'high', 'urgent'
    status: str = Field(default='pending', max_length=50)  # 'pending', 'in_progress', 'resolved', 'cancelled'
    assigned_to: Optional[str] = Field(None, max_length=255)
    resolution_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    assigned_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QueryAnalytics(BaseModel):
    """Query analytics model for performance monitoring."""

    id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    message_id: Optional[UUID] = None
    intent: Optional[str] = Field(None, max_length=100)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    escalated: bool = False
    response_time_ms: Optional[int] = Field(None, ge=0)
    llm_model: Optional[str] = Field(None, max_length=100)
    llm_tokens_input: Optional[int] = Field(None, ge=0)
    llm_tokens_output: Optional[int] = Field(None, ge=0)
    rag_retrieved_chunks: Optional[int] = Field(None, ge=0)
    identity_match_method: Optional[str] = Field(None, max_length=50)
    success: bool = True
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
