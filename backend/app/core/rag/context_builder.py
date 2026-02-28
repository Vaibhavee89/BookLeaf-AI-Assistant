"""Context assembly service for RAG-based responses."""

from typing import List, Dict, Any, Optional
import structlog
import tiktoken

from app.config import settings

logger = structlog.get_logger(__name__)


class ContextBuilder:
    """Service for assembling context from retrieved chunks."""

    def __init__(self):
        """Initialize the context builder."""
        self.max_tokens = settings.rag_max_context_tokens
        self.encoding = tiktoken.encoding_for_model("gpt-4")

        logger.info(
            "context_builder_initialized",
            max_tokens=self.max_tokens
        )

    def build_context(
        self,
        retrieved_chunks: List[Dict[str, Any]],
        query: str,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build context from retrieved chunks with deduplication and token management.

        Args:
            retrieved_chunks: List of retrieved chunks with similarity scores
            query: Original user query
            max_tokens: Maximum context tokens (default from config)

        Returns:
            Dictionary with assembled context, sources, and metadata
        """
        if not retrieved_chunks:
            logger.warning("no_chunks_provided_for_context")
            return {
                "context_text": "",
                "sources": [],
                "total_chunks": 0,
                "total_tokens": 0,
                "truncated": False
            }

        token_limit = max_tokens or self.max_tokens

        logger.info(
            "building_context",
            num_chunks=len(retrieved_chunks),
            token_limit=token_limit
        )

        # Deduplicate and rank chunks
        deduplicated_chunks = self._deduplicate_chunks(retrieved_chunks)

        # Filter by relevance
        relevant_chunks = self._filter_by_relevance(
            deduplicated_chunks,
            min_similarity=0.7
        )

        # Assemble context within token limit
        context_data = self._assemble_context(
            relevant_chunks,
            token_limit
        )

        # Add source attribution
        context_data["sources"] = self._extract_sources(context_data["chunks_used"])

        logger.info(
            "context_built",
            total_chunks=context_data["total_chunks"],
            chunks_used=len(context_data["chunks_used"]),
            total_tokens=context_data["total_tokens"],
            truncated=context_data["truncated"]
        )

        return context_data

    def _deduplicate_chunks(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate or highly similar chunks.

        Args:
            chunks: List of retrieved chunks

        Returns:
            Deduplicated list of chunks
        """
        seen_texts = set()
        deduplicated = []

        for chunk in chunks:
            # Normalize text for comparison
            normalized_text = chunk.get("chunk_text", "").strip().lower()

            # Check for exact duplicates
            if normalized_text in seen_texts:
                logger.debug(
                    "duplicate_chunk_removed",
                    chunk_id=chunk.get("chunk_id")
                )
                continue

            seen_texts.add(normalized_text)
            deduplicated.append(chunk)

        logger.debug(
            "deduplication_completed",
            original_count=len(chunks),
            deduplicated_count=len(deduplicated)
        )

        return deduplicated

    def _filter_by_relevance(
        self,
        chunks: List[Dict[str, Any]],
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Filter chunks below relevance threshold.

        Args:
            chunks: List of chunks
            min_similarity: Minimum similarity score

        Returns:
            Filtered list of relevant chunks
        """
        relevant = [
            chunk for chunk in chunks
            if chunk.get("similarity", 0) >= min_similarity
        ]

        filtered_count = len(chunks) - len(relevant)
        if filtered_count > 0:
            logger.debug(
                "low_relevance_chunks_filtered",
                filtered_count=filtered_count,
                min_similarity=min_similarity
            )

        return relevant

    def _assemble_context(
        self,
        chunks: List[Dict[str, Any]],
        token_limit: int
    ) -> Dict[str, Any]:
        """
        Assemble context text from chunks within token limit.

        Args:
            chunks: List of relevant chunks
            token_limit: Maximum tokens allowed

        Returns:
            Dictionary with context text and metadata
        """
        context_parts = []
        chunks_used = []
        total_tokens = 0
        truncated = False

        # Sort by similarity (highest first)
        sorted_chunks = sorted(
            chunks,
            key=lambda x: x.get("similarity", 0),
            reverse=True
        )

        for i, chunk in enumerate(sorted_chunks):
            chunk_text = chunk.get("chunk_text", "")

            # Add source attribution
            doc_title = chunk.get("document_title", "Unknown Document")
            formatted_chunk = f"[Source: {doc_title}]\n{chunk_text}\n"

            # Count tokens
            chunk_tokens = len(self.encoding.encode(formatted_chunk))

            # Check if adding this chunk would exceed limit
            if total_tokens + chunk_tokens > token_limit:
                logger.debug(
                    "token_limit_reached",
                    chunks_processed=i,
                    total_chunks=len(sorted_chunks)
                )
                truncated = True
                break

            context_parts.append(formatted_chunk)
            chunks_used.append(chunk)
            total_tokens += chunk_tokens

        # Join all parts
        context_text = "\n---\n".join(context_parts)

        return {
            "context_text": context_text,
            "chunks_used": chunks_used,
            "total_chunks": len(chunks),
            "chunks_included": len(chunks_used),
            "total_tokens": total_tokens,
            "truncated": truncated
        }

    def _extract_sources(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract unique sources from chunks.

        Args:
            chunks: List of chunks used in context

        Returns:
            List of unique source documents with metadata
        """
        sources_dict = {}

        for chunk in chunks:
            doc_id = chunk.get("document_id")
            if not doc_id:
                continue

            if doc_id not in sources_dict:
                sources_dict[doc_id] = {
                    "document_id": doc_id,
                    "title": chunk.get("document_title", "Unknown"),
                    "document_type": chunk.get("document_type"),
                    "chunk_count": 0,
                    "avg_similarity": 0.0,
                    "similarities": []
                }

            sources_dict[doc_id]["chunk_count"] += 1
            sources_dict[doc_id]["similarities"].append(
                chunk.get("similarity", 0)
            )

        # Calculate average similarity per document
        sources = []
        for source in sources_dict.values():
            if source["similarities"]:
                source["avg_similarity"] = sum(source["similarities"]) / len(source["similarities"])
                del source["similarities"]  # Remove temporary field

            sources.append(source)

        # Sort by relevance (avg similarity)
        sources.sort(key=lambda x: x["avg_similarity"], reverse=True)

        return sources

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))


# Global instance
_context_builder: Optional[ContextBuilder] = None


def get_context_builder() -> ContextBuilder:
    """
    Get or create global context builder instance.

    Returns:
        ContextBuilder instance
    """
    global _context_builder

    if _context_builder is None:
        _context_builder = ContextBuilder()

    return _context_builder
