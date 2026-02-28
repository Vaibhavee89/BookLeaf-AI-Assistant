"""FastAPI application entry point for BookLeaf AI Assistant."""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings


# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info(
        "application_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment
    )

    # Verify critical configurations
    if not settings.openai_api_key:
        logger.error("openai_api_key_missing")
        raise ValueError("OPENAI_API_KEY must be set")

    if not settings.supabase_url or not settings.supabase_key:
        logger.error("supabase_configuration_missing")
        raise ValueError("Supabase configuration must be set")

    logger.info("configuration_verified", models={
        "primary": settings.primary_model,
        "fallback": settings.fallback_model,
        "classification": settings.classification_model,
        "embedding": settings.embedding_model
    })

    yield

    # Shutdown
    logger.info("application_shutdown")


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered customer support system with identity unification, RAG, and intelligent routing",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning application info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "operational",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": settings.app_version
    }


# API v1 routes
from app.api.v1 import chat, identity, escalation, analytics

app.include_router(chat.router, prefix=f"{settings.api_v1_prefix}/chat", tags=["chat"])
app.include_router(identity.router, prefix=f"{settings.api_v1_prefix}/identity", tags=["identity"])
app.include_router(escalation.router, prefix=f"{settings.api_v1_prefix}/escalations", tags=["escalation"])
app.include_router(analytics.router, prefix=f"{settings.api_v1_prefix}/analytics", tags=["analytics"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=exc
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "path": request.url.path
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
