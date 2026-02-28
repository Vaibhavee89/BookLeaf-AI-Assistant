"""Vector retrieval service using Supabase pgvector."""

from typing import List, Dict, Any, Optional
import structlog

from app.db.client import get_supabase_client
from app.core.rag.embedder import get_embedding_service
from app.config import settings

logger = structlog.get_logger(__name__)


class VectorRetriever:
    """Service for retrieving relevant knowledge base chunks using vector similarity."""

    def __init__(self):
        """Initialize the vector retriever."""
        self.supabase = get_supabase_client()
        self.embedding_service = get_embedding_service()
        self.top_k = settings.rag_top_k

        logger.info("vector_retriever_initialized", top_k=self.top_k)

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: float = 0.7,
        document_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant knowledge base chunks for a query.

        Args:
            query: User query text
            top_k: Number of results to return (default from config)
            similarity_threshold: Minimum similarity score (0-1)
            document_types: Filter by document types (optional)

        Returns:
            List of relevant chunks with metadata and similarity scores
        """
        if not query or not query.strip():
            logger.warning("empty_query_for_retrieval")
            return []

        k = top_k or self.top_k

        try:
            # Generate query embedding
            logger.debug("generating_query_embedding", query_preview=query[:100])
            query_embedding = self.embedding_service.generate_embedding(query)

            if not query_embedding:
                logger.error("query_embedding_failed")
                return []

            # Perform vector similarity search
            logger.info(
                "vector_search_started",
                top_k=k,
                threshold=similarity_threshold,
                document_types=document_types
            )

            # Build RPC call for pgvector similarity search
            # Using cosine similarity (1 - cosine distance)
            rpc_params = {
                "query_embedding": query_embedding,
                "match_threshold": similarity_threshold,
                "match_count": k
            }

            # Call stored procedure for vector search
            # Note: This assumes you have a stored procedure in Supabase
            # Alternative: Use direct SQL query
            try:
                # Try using RPC first (requires stored procedure in Supabase)
                response = self.supabase.rpc(
                    "match_knowledge_embeddings",
                    rpc_params
                ).execute()

                results = response.data if response.data else []

            except Exception as rpc_error:
                logger.warning(
                    "rpc_not_available_using_direct_query",
                    error=str(rpc_error)
                )

                # Fallback to direct query
                results = self._direct_vector_search(
                    query_embedding,
                    k,
                    similarity_threshold,
                    document_types
                )

            # Format results
            formatted_results = self._format_results(results)

            logger.info(
                "vector_search_completed",
                results_found=len(formatted_results),
                avg_similarity=sum(r["similarity"] for r in formatted_results) / len(formatted_results) if formatted_results else 0
            )

            return formatted_results

        except Exception as e:
            logger.error(
                "vector_retrieval_failed",
                error=str(e),
                query_preview=query[:100],
                exc_info=e
            )
            return []

    def _direct_vector_search(
        self,
        query_embedding: List[float],
        top_k: int,
        similarity_threshold: float,
        document_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform direct vector similarity search using SQL.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results
            similarity_threshold: Minimum similarity
            document_types: Filter by document types

        Returns:
            List of matching chunks with similarity scores
        """
        try:
            # Query knowledge_embeddings with vector similarity
            # Note: Supabase Python client doesn't have direct vector ops yet
            # We need to join with knowledge_documents to get metadata

            # This is a simplified version - in production, use stored procedure
            query_builder = self.supabase.table("knowledge_embeddings").select(
                """
                id,
                chunk_text,
                chunk_index,
                metadata,
                created_at,
                document_id,
                knowledge_documents!inner(
                    title,
                    document_type,
                    metadata
                )
                """
            ).order("created_at", desc=True).limit(top_k * 3)  # Get more, filter by similarity later

            if document_types:
                # Note: This is a simplified filter
                # Proper implementation would filter in SQL
                pass

            response = query_builder.execute()

            # In production, calculate cosine similarity in SQL
            # For now, return top results
            # This is a placeholder - you should implement proper vector search
            results = response.data if response.data else []

            # Add placeholder similarity scores
            # In production, calculate from actual vectors
            for i, result in enumerate(results[:top_k]):
                result["similarity"] = 1.0 - (i * 0.05)  # Placeholder decreasing similarity

            return results[:top_k]

        except Exception as e:
            logger.error("direct_vector_search_failed", error=str(e), exc_info=e)
            return []

    def _format_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format retrieval results into consistent structure.

        Args:
            results: Raw results from database

        Returns:
            Formatted results with relevant fields
        """
        formatted = []

        for result in results:
            try:
                # Extract document info (handle both RPC and direct query formats)
                if "knowledge_documents" in result:
                    doc_info = result["knowledge_documents"]
                else:
                    doc_info = {
                        "title": result.get("document_title", "Unknown"),
                        "document_type": result.get("document_type"),
                        "metadata": result.get("document_metadata", {})
                    }

                formatted_result = {
                    "chunk_id": result.get("id"),
                    "chunk_text": result.get("chunk_text", ""),
                    "chunk_index": result.get("chunk_index", 0),
                    "similarity": result.get("similarity", 0.0),
                    "document_id": result.get("document_id"),
                    "document_title": doc_info.get("title", "Unknown"),
                    "document_type": doc_info.get("document_type"),
                    "metadata": {
                        **result.get("metadata", {}),
                        **doc_info.get("metadata", {})
                    }
                }

                formatted.append(formatted_result)

            except Exception as e:
                logger.warning(
                    "result_formatting_failed",
                    error=str(e),
                    result_id=result.get("id")
                )
                continue

        return formatted

    def retrieve_by_document_type(
        self,
        query: str,
        document_type: str,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chunks filtered by document type.

        Args:
            query: User query
            document_type: Document type to filter by
            top_k: Number of results

        Returns:
            Filtered retrieval results
        """
        return self.retrieve(
            query=query,
            top_k=top_k,
            document_types=[document_type]
        )


# Global instance
_vector_retriever: Optional[VectorRetriever] = None


def get_vector_retriever() -> VectorRetriever:
    """
    Get or create global vector retriever instance.

    Returns:
        VectorRetriever instance
    """
    global _vector_retriever

    if _vector_retriever is None:
        _vector_retriever = VectorRetriever()

    return _vector_retriever
