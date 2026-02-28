"""Database client initialization and management with local fallback."""

from functools import lru_cache
import structlog

logger = structlog.get_logger(__name__)

# Try to import Supabase, fallback to local if it fails
_USE_LOCAL_DB = False
_db_client = None

try:
    from supabase import create_client, Client
    from app.config import settings

    # Try to create Supabase client
    if settings.supabase_url and settings.supabase_key:
        try:
            _db_client = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key
            )
            # Test connection
            _db_client.table("authors").select("id").limit(1).execute()
            logger.info("supabase_client_initialized", url=settings.supabase_url)
        except Exception as e:
            logger.warning("supabase_connection_failed", error=str(e))
            _USE_LOCAL_DB = True
    else:
        logger.warning("supabase_credentials_missing")
        _USE_LOCAL_DB = True

except Exception as e:
    logger.warning("supabase_import_failed", error=str(e))
    _USE_LOCAL_DB = True

# Use local database if Supabase is not available
if _USE_LOCAL_DB or _db_client is None:
    from app.db.local_client import local_db
    _db_client = local_db
    logger.info("using_local_database_fallback")


@lru_cache()
def get_db_client():
    """
    Get database client (Supabase or local fallback).

    Returns:
        Database client instance
    """
    return _db_client


def get_db():
    """
    Dependency function for FastAPI to inject database client.

    Returns:
        Database client instance
    """
    return get_db_client()


def is_using_local_db() -> bool:
    """Check if using local database."""
    return _USE_LOCAL_DB


# Global client instance for non-FastAPI code
supabase = _db_client

# Alias for compatibility
db = _db_client
get_supabase_client = get_db_client  # Alias for backward compatibility
