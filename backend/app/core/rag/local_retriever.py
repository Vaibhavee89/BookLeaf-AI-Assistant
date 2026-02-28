"""Local knowledge base retriever using keyword-based search (no vector embeddings)."""

from typing import List, Dict, Any
import re
import structlog

from app.db.local_client import local_db

logger = structlog.get_logger(__name__)


class LocalRAGRetriever:
    """Simple keyword-based retriever for local knowledge base."""

    def __init__(self):
        """Initialize the local retriever."""
        self.top_k = 5
        logger.info("local_rag_retriever_initialized")

    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract keywords from query.

        Args:
            query: User query text

        Returns:
            List of keywords
        """
        # Remove common words (stop words)
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'i', 'my', 'me', 'you', 'your',
            'when', 'where', 'who', 'what', 'why', 'how', 'can', 'could',
            'should', 'would', 'do', 'does', 'did'
        }

        # Convert to lowercase and split
        words = re.findall(r'\b\w+\b', query.lower())

        # Filter out stop words and short words
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        logger.debug("keywords_extracted", query=query, keywords=keywords)

        return keywords

    def search_chunks(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Search knowledge base chunks for keywords.

        Args:
            keywords: List of keywords to search

        Returns:
            List of matching chunks with scores
        """
        try:
            # Get all chunks
            result = local_db.table("knowledge_embeddings").select("*").execute()

            if not result.data:
                logger.warning("no_chunks_found")
                return []

            chunks = result.data
            scored_chunks = []

            # Score each chunk based on keyword matches
            for chunk in chunks:
                chunk_text = chunk.get("chunk_text", "").lower()
                score = 0

                for keyword in keywords:
                    # Count occurrences of keyword
                    count = chunk_text.count(keyword)
                    if count > 0:
                        # Weight by frequency (with diminishing returns)
                        score += min(count, 3)

                        # Bonus for exact phrase match
                        if f" {keyword} " in f" {chunk_text} ":
                            score += 1

                if score > 0:
                    # Get document info
                    doc_result = local_db.table("knowledge_documents").select("*").eq("id", chunk["document_id"]).single().execute()

                    chunk_with_score = {
                        **chunk,
                        "score": score,
                        "document": doc_result.data if doc_result.data else {}
                    }
                    scored_chunks.append(chunk_with_score)

            # Sort by score (descending)
            scored_chunks.sort(key=lambda x: x["score"], reverse=True)

            # Return top K
            top_chunks = scored_chunks[:self.top_k]

            logger.info(
                "chunks_retrieved",
                total_matches=len(scored_chunks),
                returned=len(top_chunks)
            )

            return top_chunks

        except Exception as e:
            logger.error("chunk_search_failed", error=str(e), exc_info=e)
            return []

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge base chunks for a query.

        Args:
            query: User query text
            top_k: Number of chunks to return

        Returns:
            List of relevant chunks with metadata
        """
        self.top_k = top_k

        logger.info("retrieving_knowledge", query=query, top_k=top_k)

        # Extract keywords
        keywords = self.extract_keywords(query)

        if not keywords:
            logger.warning("no_keywords_extracted", query=query)
            return []

        # Search chunks
        chunks = self.search_chunks(keywords)

        # Format results
        results = []
        for chunk in chunks:
            results.append({
                "chunk_text": chunk["chunk_text"],
                "chunk_index": chunk["chunk_index"],
                "score": chunk["score"],
                "document_title": chunk.get("document", {}).get("title", "Unknown"),
                "document_type": chunk.get("document", {}).get("document_type", "unknown"),
                "metadata": chunk.get("metadata", {})
            })

        logger.info(
            "knowledge_retrieved",
            query=query,
            results_count=len(results)
        )

        return results

    def build_context(self, chunks: List[Dict[str, Any]], max_tokens: int = 2000) -> str:
        """
        Build context string from retrieved chunks.

        Args:
            chunks: Retrieved chunks
            max_tokens: Maximum tokens (approximated as characters / 4)

        Returns:
            Formatted context string
        """
        if not chunks:
            return ""

        context_parts = []
        current_length = 0
        max_chars = max_tokens * 4  # Rough approximation

        for chunk in chunks:
            chunk_text = chunk["chunk_text"]
            doc_title = chunk.get("document_title", "Unknown")

            # Format chunk with source attribution
            formatted = f"From \"{doc_title}\":\n{chunk_text}\n"

            # Check if adding this chunk would exceed limit
            if current_length + len(formatted) > max_chars:
                break

            context_parts.append(formatted)
            current_length += len(formatted)

        context = "\n---\n\n".join(context_parts)

        logger.info(
            "context_built",
            chunks_used=len(context_parts),
            total_chars=len(context)
        )

        return context


# Global instance
local_rag_retriever = LocalRAGRetriever()
