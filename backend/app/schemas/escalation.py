"""Pydantic schemas for escalation-related endpoints."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class Escalation(BaseModel):
    """Escalation model."""

    id: str
    conversation_id: str
    message_id: Optional[str]
    reason: str
    priority: str = Field(..., description="low, medium, high, or urgent")
    status: str = Field(..., description="pending, in_progress, resolved, or cancelled")
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    assigned_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EscalationListResponse(BaseModel):
    """Response model for escalation list."""

    escalations: List[Escalation]
    count: int
    pending_count: int
    in_progress_count: int


class EscalationUpdateRequest(BaseModel):
    """Request model for updating escalation."""

    status: Optional[str] = Field(None, description="pending, in_progress, resolved, or cancelled")
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    priority: Optional[str] = Field(None, description="low, medium, high, or urgent")


class EscalationResolveRequest(BaseModel):
    """Request model for resolving escalation."""

    resolution_notes: str = Field(..., min_length=1, max_length=2000)
