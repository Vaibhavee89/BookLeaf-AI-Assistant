"""Identity API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
import structlog

from app.schemas.identity import (
    IdentityResolveRequest,
    IdentityResolveResponse,
    IdentityListResponse
)
from app.services.identity_service import get_identity_service
from app.db.client import get_db, Client

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/resolve", response_model=IdentityResolveResponse)
async def resolve_identity(
    request: IdentityResolveRequest,
    db: Client = Depends(get_db)
):
    """
    Resolve identity from provided information.

    Uses multi-stage matching: exact → fuzzy → LLM → create new.
    """
    try:
        identity_service = get_identity_service()

        result = identity_service.resolve_identity(
            name=request.name,
            email=request.email,
            phone=request.phone,
            platform=request.platform,
            context=request.context
        )

        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Identity resolution failed")
            )

        return IdentityResolveResponse(
            success=result["success"],
            author=result["author"],
            identity=result["identity"],
            confidence=result["confidence"],
            method=result["method"],
            reasoning=result["reasoning"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("identity_resolution_error", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resolve identity: {str(e)}"
        )


@router.get("/author/{author_id}", response_model=IdentityListResponse)
async def get_author_identities(
    author_id: str,
    db: Client = Depends(get_db)
):
    """
    Get all identities for an author.

    Returns all platform identities linked to an author.
    """
    try:
        response = db.table("identities").select(
            "*"
        ).eq("author_id", author_id).execute()

        identities = response.data if response.data else []

        return IdentityListResponse(
            identities=identities,
            count=len(identities)
        )

    except Exception as e:
        logger.error("identities_retrieval_error", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve identities: {str(e)}"
        )
