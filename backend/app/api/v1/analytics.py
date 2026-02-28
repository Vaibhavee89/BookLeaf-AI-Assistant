"""Analytics API endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
import structlog

from app.db.client import get_db, Client

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/stats")
async def get_stats(
    db: Client = Depends(get_db)
):
    """
    Get aggregate statistics.

    Returns overall system metrics.
    """
    try:
        # Get query analytics stats
        analytics_response = db.table("query_analytics").select("*").execute()
        analytics = analytics_response.data if analytics_response.data else []

        # Get escalation stats
        escalations_response = db.table("escalations").select("status").execute()
        escalations = escalations_response.data if escalations_response.data else []

        # Calculate metrics
        total_queries = len(analytics)
        successful_queries = len([a for a in analytics if a.get("success")])
        escalated_queries = len([a for a in analytics if a.get("escalated")])

        avg_confidence = (
            sum(a.get("confidence_score", 0) for a in analytics if a.get("confidence_score")) / len(analytics)
            if analytics else 0
        )

        avg_response_time = (
            sum(a.get("response_time_ms", 0) for a in analytics if a.get("response_time_ms")) / len(analytics)
            if analytics else 0
        )

        pending_escalations = len([e for e in escalations if e.get("status") == "pending"])
        resolved_escalations = len([e for e in escalations if e.get("status") == "resolved"])

        # Intent distribution
        intent_counts = {}
        for a in analytics:
            intent = a.get("intent", "unknown")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "failed_queries": total_queries - successful_queries,
            "escalated_queries": escalated_queries,
            "escalation_rate": escalated_queries / total_queries if total_queries > 0 else 0,
            "average_confidence": round(avg_confidence, 3),
            "average_response_time_ms": round(avg_response_time, 0),
            "pending_escalations": pending_escalations,
            "resolved_escalations": resolved_escalations,
            "intent_distribution": intent_counts
        }

    except Exception as e:
        logger.error("stats_retrieval_error", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve stats: {str(e)}"
        )


@router.get("/confidence-distribution")
async def get_confidence_distribution(
    db: Client = Depends(get_db)
):
    """
    Get confidence score distribution.

    Returns histogram of confidence scores.
    """
    try:
        response = db.table("query_analytics").select("confidence_score").execute()
        scores = [a.get("confidence_score") for a in (response.data or []) if a.get("confidence_score") is not None]

        if not scores:
            return {
                "total_count": 0,
                "bins": []
            }

        # Create bins: 0-0.2, 0.2-0.4, 0.4-0.6, 0.6-0.8, 0.8-1.0
        bins = {
            "0.0-0.2": 0,
            "0.2-0.4": 0,
            "0.4-0.6": 0,
            "0.6-0.8": 0,
            "0.8-1.0": 0
        }

        for score in scores:
            if score < 0.2:
                bins["0.0-0.2"] += 1
            elif score < 0.4:
                bins["0.2-0.4"] += 1
            elif score < 0.6:
                bins["0.4-0.6"] += 1
            elif score < 0.8:
                bins["0.6-0.8"] += 1
            else:
                bins["0.8-1.0"] += 1

        return {
            "total_count": len(scores),
            "bins": [{"range": k, "count": v} for k, v in bins.items()]
        }

    except Exception as e:
        logger.error("confidence_distribution_error", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve confidence distribution: {str(e)}"
        )
