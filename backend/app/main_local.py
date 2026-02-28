"""FastAPI application with local database support (no Supabase/OpenAI required)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.api.v1 import local_chat

logger = structlog.get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BookLeaf AI Assistant (Local Mode)",
    description="Multi-channel query responder with local SQLite database",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(local_chat.router, prefix="/api/v1", tags=["chat"])


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("application_starting", mode="local")
    print("\n" + "="*60)
    print("🚀 BookLeaf AI Assistant - Local Mode")
    print("="*60)
    print("✓ Using local SQLite database")
    print("✓ No Supabase connection required")
    print("✓ No OpenAI API required")
    print("✓ Keyword-based knowledge retrieval")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("application_shutting_down")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "BookLeaf AI Assistant API (Local Mode)",
        "version": "1.0.0",
        "mode": "local",
        "docs_url": "/docs",
        "health_url": "/api/v1/health"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return await local_chat.health_check()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
