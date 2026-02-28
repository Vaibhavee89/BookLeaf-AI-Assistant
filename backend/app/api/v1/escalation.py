"""Escalation API endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
import structlog

from app.schemas.escalation import (
    Escalation,
    EscalationListResponse,
    EscalationUpdateRequest,
    EscalationResolveRequest
)
from app.db.client import get_db, Client

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=EscalationListResponse)
async def list_escalations(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    limit: int = Query(50, ge=1, le=200),
    db: Client = Depends(get_db)
):
    """
    List escalations with optional filtering.

    Returns pending and in-progress escalations for the support queue.
    """
    try:
        query = db.table("escalations").select("*").order("created_at", desc=True)

        if status:
            query = query.eq("status", status)

        if priority:
            query = query.eq("priority", priority)

        query = query.limit(limit)

        response = query.execute()

        escalations = response.data if response.data else []

        # Count by status
        pending_count = len([e for e in escalations if e.get("status") == "pending"])
        in_progress_count = len([e for e in escalations if e.get("status") == "in_progress"])

        return EscalationListResponse(
            escalations=escalations,
            count=len(escalations),
            pending_count=pending_count,
            in_progress_count=in_progress_count
        )

    except Exception as e:
        logger.error("escalations_list_error", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve escalations: {str(e)}"
        )


@router.get("/{escalation_id}", response_model=Escalation)
async def get_escalation(
    escalation_id: str,
    db: Client = Depends(get_db)
):
    """Get escalation details by ID."""
    try:
        response = db.table("escalations").select(
            "*"
        ).eq("id", escalation_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=f"Escalation {escalation_id} not found"
            )

        return Escalation(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error("escalation_retrieval_error", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve escalation: {str(e)}"
        )


@router.patch("/{escalation_id}", response_model=Escalation)
async def update_escalation(
    escalation_id: str,
    request: EscalationUpdateRequest,
    db: Client = Depends(get_db)
):
    """Update escalation status, assignment, or priority."""
    try:
        # Build update data
        update_data = {}

        if request.status is not None:
            update_data["status"] = request.status

        if request.assigned_to is not None:
            update_data["assigned_to"] = request.assigned_to
            if not update_data.get("status"):
                update_data["status"] = "in_progress"

        if request.resolution_notes is not None:
            update_data["resolution_notes"] = request.resolution_notes

        if request.priority is not None:
            update_data["priority"] = request.priority

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No update fields provided"
            )

        # Update escalation
        response = db.table("escalations").update(
            update_data
        ).eq("id", escalation_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=f"Escalation {escalation_id} not found"
            )

        logger.info("escalation_updated", escalation_id=escalation_id)

        return Escalation(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error("escalation_update_error", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update escalation: {str(e)}"
        )


@router.post("/{escalation_id}/resolve", response_model=Escalation)
async def resolve_escalation(
    escalation_id: str,
    request: EscalationResolveRequest,
    db: Client = Depends(get_db)
):
    """Resolve an escalation with notes."""
    try:
        from datetime import datetime

        response = db.table("escalations").update({
            "status": "resolved",
            "resolution_notes": request.resolution_notes,
            "resolved_at": datetime.utcnow().isoformat()
        }).eq("id", escalation_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=f"Escalation {escalation_id} not found"
            )

        logger.info("escalation_resolved", escalation_id=escalation_id)

        return Escalation(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error("escalation_resolve_error", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resolve escalation: {str(e)}"
        )
