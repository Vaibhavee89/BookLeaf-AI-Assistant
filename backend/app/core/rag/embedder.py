"""Embedding generation service using OpenAI API."""

from typing import List, Optional
import openai
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = structlog.get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using OpenAI."""

    def __init__(self):
        """Initialize the embedding service."""
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model
        self.dimensions = settings.embedding_dimensions

        logger.info(
            "embedding_service_initialized",
            model=self.model,
            dimensions=self.dimensions
        )

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector, or None if failed

        Raises:
            Exception: If embedding generation fails after retries
        """
        if not text or not text.strip():
            logger.warning("empty_text_for_embedding")
            return None

        try:
            # Clean and prepare text
            cleaned_text = text.strip().replace("\n", " ")

            # Generate embedding
            response = self.client.embeddings.create(
                input=cleaned_text,
                model=self.model,
                dimensions=self.dimensions
            )

            embedding = response.data[0].embedding

            logger.debug(
                "embedding_generated",
                text_length=len(cleaned_text),
                embedding_dimension=len(embedding)
            )

            return embedding

        except openai.RateLimitError as e:
            logger.error("rate_limit_exceeded", error=str(e))
            raise
        except openai.APIError as e:
            logger.error("openai_api_error", error=str(e))
            raise
        except Exception as e:
            logger.error(
                "embedding_generation_failed",
                error=str(e),
                text_preview=text[:100] if text else None,
                exc_info=e
            )
            raise

    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of input texts
            batch_size: Number of texts to process per batch (OpenAI limit is 2048)

        Returns:
            List of embedding vectors (same length as input texts)
        """
        if not texts:
            logger.warning("empty_texts_list_for_batch_embedding")
            return []

        logger.info(
            "batch_embedding_started",
            total_texts=len(texts),
            batch_size=batch_size
        )

        all_embeddings = []
        failed_count = 0

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(texts) + batch_size - 1) // batch_size

            logger.info(
                "processing_batch",
                batch_num=batch_num,
                total_batches=total_batches,
                batch_size=len(batch)
            )

            try:
                # Clean texts
                cleaned_batch = [text.strip().replace("\n", " ") for text in batch]

                # Generate embeddings for batch
                response = self.client.embeddings.create(
                    input=cleaned_batch,
                    model=self.model,
                    dimensions=self.dimensions
                )

                # Extract embeddings
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

                logger.info(
                    "batch_completed",
                    batch_num=batch_num,
                    embeddings_generated=len(batch_embeddings)
                )

            except Exception as e:
                logger.error(
                    "batch_embedding_failed",
                    batch_num=batch_num,
                    error=str(e),
                    exc_info=e
                )

                # Add None for failed embeddings
                all_embeddings.extend([None] * len(batch))
                failed_count += len(batch)

        logger.info(
            "batch_embedding_completed",
            total_embeddings=len(all_embeddings),
            successful=len(all_embeddings) - failed_count,
            failed=failed_count
        )

        return all_embeddings

    async def generate_embedding_async(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding asynchronously (for async contexts).

        Args:
            text: Input text to embed

        Returns:
            Embedding vector or None if failed
        """
        # For now, call synchronous version
        # Can be replaced with async OpenAI client in future
        return self.generate_embedding(text)


# Global instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Get or create global embedding service instance.

    Returns:
        EmbeddingService instance
    """
    global _embedding_service

    if _embedding_service is None:
        _embedding_service = EmbeddingService()

    return _embedding_service
