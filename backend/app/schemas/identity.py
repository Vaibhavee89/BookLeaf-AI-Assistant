"""Pydantic schemas for identity-related endpoints."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class IdentityResolveRequest(BaseModel):
    """Request model for identity resolution."""

    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    platform: str = Field(default="web_chat", max_length=50)
    context: Optional[str] = Field(None, max_length=1000, description="Conversation context for disambiguation")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sarah Johnson",
                "email": "sarah.j@email.com",
                "platform": "web_chat"
            }
        }


class IdentityProfile(BaseModel):
    """Identity profile response."""

    id: str
    author_id: str
    platform: str
    platform_identifier: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    matching_method: str
    verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AuthorProfile(BaseModel):
    """Author profile response."""

    id: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class IdentityResolveResponse(BaseModel):
    """Response model for identity resolution."""

    success: bool
    author: Optional[AuthorProfile]
    identity: Optional[IdentityProfile]
    confidence: float = Field(..., ge=0.0, le=1.0)
    method: str
    reasoning: str


class IdentityListResponse(BaseModel):
    """Response model for listing identities."""

    identities: List[IdentityProfile]
    count: int
