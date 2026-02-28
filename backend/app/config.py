"""Application configuration management using Pydantic Settings."""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Settings
    app_name: str = Field(default="BookLeaf AI Assistant")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")

    # API Settings
    api_v1_prefix: str = Field(default="/api/v1")
    cors_origins: List[str] = Field(default=["http://localhost:3000"])

    # OpenAI Configuration
    openai_api_key: str = Field(...)
    primary_model: str = Field(default="gpt-4-turbo-preview")
    fallback_model: str = Field(default="gpt-4")
    classification_model: str = Field(default="gpt-4o-mini")
    embedding_model: str = Field(default="text-embedding-3-large")
    embedding_dimensions: int = Field(default=1536)

    # Supabase Configuration
    supabase_url: str = Field(...)
    supabase_key: str = Field(...)
    supabase_service_role_key: str = Field(...)

    # Confidence Thresholds
    confidence_threshold_auto_respond: float = Field(default=0.80)
    confidence_threshold_escalate: float = Field(default=0.80)

    # RAG Configuration
    rag_top_k: int = Field(default=5)
    rag_chunk_size: int = Field(default=500)
    rag_chunk_overlap: int = Field(default=50)
    rag_max_context_tokens: int = Field(default=8000)

    # Identity Matching Configuration
    fuzzy_match_threshold: int = Field(default=85)
    identity_confidence_weight: float = Field(default=0.30)
    intent_confidence_weight: float = Field(default=0.20)
    rag_confidence_weight: float = Field(default=0.25)
    llm_confidence_weight: float = Field(default=0.25)

    # Rate Limiting
    max_retries: int = Field(default=3)
    retry_delay: float = Field(default=1.0)
    request_timeout: float = Field(default=30.0)

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def confidence_weights(self) -> dict:
        """Get confidence calculation weights."""
        return {
            "identity": self.identity_confidence_weight,
            "intent": self.intent_confidence_weight,
            "rag": self.rag_confidence_weight,
            "llm": self.llm_confidence_weight
        }


# Global settings instance
settings = Settings()
