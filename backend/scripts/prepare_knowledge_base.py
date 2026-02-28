"""Script to prepare knowledge base: chunk documents and generate embeddings."""

import sys
import os
from pathlib import Path
import re
from typing import List, Dict, Any

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.db.client import supabase
from app.core.rag.embedder import get_embedding_service
from app.config import settings
import structlog
import tiktoken

logger = structlog.get_logger(__name__)


class KnowledgeBasePreparator:
    """Service to prepare knowledge base documents for RAG."""

    def __init__(self):
        """Initialize the preparator."""
        self.embedding_service = get_embedding_service()
        self.chunk_size = settings.rag_chunk_size
        self.chunk_overlap = settings.rag_chunk_overlap
        self.encoding = tiktoken.encoding_for_model("gpt-4")

        self.knowledge_base_dir = Path(__file__).parent.parent.parent / "knowledge-base"

        logger.info(
            "preparator_initialized",
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap,
            knowledge_base_dir=str(self.knowledge_base_dir)
        )

    def load_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Load a markdown document from file.

        Args:
            file_path: Path to markdown file

        Returns:
            Dictionary with document metadata and content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title from filename or first H1
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem.replace('_', ' ').title()

            # Determine document type from filename
            doc_type = file_path.stem

            logger.info(
                "document_loaded",
                file=file_path.name,
                title=title,
                content_length=len(content)
            )

            return {
                "file_path": str(file_path),
                "title": title,
                "document_type": doc_type,
                "content": content,
                "metadata": {
                    "source_file": file_path.name,
                    "file_size": len(content)
                }
            }

        except Exception as e:
            logger.error(
                "document_load_failed",
                file=str(file_path),
                error=str(e),
                exc_info=e
            )
            return None

    def chunk_document(self, content: str) -> List[Dict[str, Any]]:
        """
        Chunk document into overlapping pieces based on token count.

        Args:
            content: Document content

        Returns:
            List of chunks with metadata
        """
        # Tokenize content
        tokens = self.encoding.encode(content)
        total_tokens = len(tokens)

        logger.info(
            "chunking_document",
            total_tokens=total_tokens,
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap
        )

        chunks = []
        chunk_index = 0
        start = 0

        while start < total_tokens:
            # Define chunk boundaries
            end = min(start + self.chunk_size, total_tokens)

            # Extract chunk tokens and decode
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)

            # Try to end chunk at sentence boundary if not at document end
            if end < total_tokens:
                # Look for sentence endings in last 100 characters
                last_part = chunk_text[-100:]
                sentence_end = max(
                    last_part.rfind('. '),
                    last_part.rfind('! '),
                    last_part.rfind('? '),
                    last_part.rfind('\n\n')
                )

                if sentence_end > 0:
                    # Adjust chunk to end at sentence
                    adjusted_text = chunk_text[:-(100 - sentence_end)]
                    chunk_text = adjusted_text
                    # Recalculate actual end position
                    end = start + len(self.encoding.encode(chunk_text))

            chunks.append({
                "chunk_index": chunk_index,
                "chunk_text": chunk_text.strip(),
                "token_count": len(chunk_tokens),
                "start_token": start,
                "end_token": end,
                "metadata": {
                    "position": f"{chunk_index + 1}/{(total_tokens + self.chunk_size - 1) // self.chunk_size}"
                }
            })

            chunk_index += 1

            # Move start position (with overlap)
            start = end - self.chunk_overlap

        logger.info(
            "chunking_completed",
            total_chunks=len(chunks),
            avg_tokens_per_chunk=sum(c["token_count"] for c in chunks) / len(chunks) if chunks else 0
        )

        return chunks

    def store_document(self, document: Dict[str, Any]) -> str:
        """
        Store document in knowledge_documents table.

        Args:
            document: Document dictionary

        Returns:
            Document ID (UUID)
        """
        try:
            result = supabase.table("knowledge_documents").insert({
                "title": document["title"],
                "document_type": document["document_type"],
                "content": document["content"],
                "metadata": document["metadata"]
            }).execute()

            if not result.data:
                logger.error("document_storage_failed", title=document["title"])
                return None

            doc_id = result.data[0]["id"]
            logger.info("document_stored", doc_id=doc_id, title=document["title"])

            return doc_id

        except Exception as e:
            logger.error(
                "document_storage_error",
                title=document["title"],
                error=str(e),
                exc_info=e
            )
            return None

    def store_embeddings(
        self,
        document_id: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> int:
        """
        Store chunk embeddings in knowledge_embeddings table.

        Args:
            document_id: Document UUID
            chunks: List of chunks
            embeddings: List of embedding vectors

        Returns:
            Number of embeddings stored
        """
        if len(chunks) != len(embeddings):
            logger.error(
                "chunk_embedding_mismatch",
                chunks=len(chunks),
                embeddings=len(embeddings)
            )
            return 0

        stored_count = 0

        for chunk, embedding in zip(chunks, embeddings):
            if embedding is None:
                logger.warning(
                    "skipping_chunk_with_null_embedding",
                    chunk_index=chunk["chunk_index"]
                )
                continue

            try:
                result = supabase.table("knowledge_embeddings").insert({
                    "document_id": document_id,
                    "chunk_text": chunk["chunk_text"],
                    "chunk_index": chunk["chunk_index"],
                    "embedding": embedding,
                    "metadata": {
                        **chunk["metadata"],
                        "token_count": chunk["token_count"]
                    }
                }).execute()

                if result.data:
                    stored_count += 1

            except Exception as e:
                logger.error(
                    "embedding_storage_failed",
                    chunk_index=chunk["chunk_index"],
                    error=str(e)
                )
                continue

        logger.info(
            "embeddings_stored",
            document_id=document_id,
            stored_count=stored_count,
            total_chunks=len(chunks)
        )

        return stored_count

    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single document: load, chunk, embed, and store.

        Args:
            file_path: Path to document file

        Returns:
            Processing result summary
        """
        logger.info("processing_document", file=file_path.name)

        # Load document
        document = self.load_document(file_path)
        if not document:
            return {"success": False, "error": "Failed to load document"}

        # Store document
        document_id = self.store_document(document)
        if not document_id:
            return {"success": False, "error": "Failed to store document"}

        # Chunk document
        chunks = self.chunk_document(document["content"])
        if not chunks:
            return {"success": False, "error": "Failed to chunk document"}

        # Generate embeddings
        logger.info("generating_embeddings", num_chunks=len(chunks))
        chunk_texts = [chunk["chunk_text"] for chunk in chunks]
        embeddings = self.embedding_service.generate_embeddings_batch(chunk_texts)

        # Store embeddings
        stored_count = self.store_embeddings(document_id, chunks, embeddings)

        result = {
            "success": True,
            "document_id": document_id,
            "title": document["title"],
            "total_chunks": len(chunks),
            "embeddings_stored": stored_count
        }

        logger.info("document_processing_completed", **result)

        return result

    def process_all_documents(self) -> Dict[str, Any]:
        """
        Process all markdown documents in knowledge base directory.

        Returns:
            Summary of processing results
        """
        if not self.knowledge_base_dir.exists():
            logger.error("knowledge_base_directory_not_found", dir=str(self.knowledge_base_dir))
            return {"success": False, "error": "Knowledge base directory not found"}

        # Find all markdown files
        md_files = list(self.knowledge_base_dir.glob("*.md"))

        logger.info(
            "processing_knowledge_base",
            total_files=len(md_files),
            directory=str(self.knowledge_base_dir)
        )

        if not md_files:
            logger.warning("no_markdown_files_found")
            return {"success": False, "error": "No markdown files found"}

        results = []
        total_chunks = 0
        total_embeddings = 0

        for md_file in md_files:
            result = self.process_document(md_file)
            results.append(result)

            if result["success"]:
                total_chunks += result["total_chunks"]
                total_embeddings += result["embeddings_stored"]

        summary = {
            "success": True,
            "documents_processed": len(results),
            "documents_successful": sum(1 for r in results if r["success"]),
            "total_chunks": total_chunks,
            "total_embeddings": total_embeddings,
            "results": results
        }

        logger.info("knowledge_base_processing_completed", **{
            k: v for k, v in summary.items() if k != "results"
        })

        return summary

    def clear_existing_data(self):
        """Clear existing knowledge base data (for re-processing)."""
        try:
            logger.warning("clearing_existing_knowledge_base")

            supabase.table("knowledge_embeddings").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            supabase.table("knowledge_documents").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

            logger.info("existing_knowledge_base_cleared")
            print("✅ Existing knowledge base data cleared\n")

        except Exception as e:
            logger.error("data_clearing_error", error=str(e))
            print(f"⚠️ Warning: Could not clear existing data: {e}\n")


def main():
    """Main function to run knowledge base preparation."""
    print("\n" + "="*60)
    print("BookLeaf AI Assistant - Knowledge Base Preparation")
    print("="*60 + "\n")

    preparator = KnowledgeBasePreparator()

    # Ask if user wants to clear existing data
    response = input("Do you want to clear existing knowledge base data? (y/N): ").strip().lower()
    if response == 'y':
        preparator.clear_existing_data()

    # Process all documents
    print("Processing knowledge base documents...\n")
    summary = preparator.process_all_documents()

    if summary["success"]:
        print("\n" + "="*60)
        print("✅ Knowledge Base Preparation Completed!")
        print("="*60)
        print(f"Documents processed: {summary['documents_processed']}")
        print(f"Documents successful: {summary['documents_successful']}")
        print(f"Total chunks: {summary['total_chunks']}")
        print(f"Total embeddings: {summary['total_embeddings']}")
        print("="*60 + "\n")

        print("Document details:")
        for result in summary["results"]:
            if result["success"]:
                print(f"  ✓ {result['title']}: {result['embeddings_stored']} embeddings")
            else:
                print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")

        print("\nYou can now verify the embeddings in your Supabase dashboard:")
        print("1. Go to Table Editor → knowledge_documents")
        print("2. Go to Table Editor → knowledge_embeddings")
        print("\nNext step: Start the backend and test the chat interface\n")

    else:
        print("\n" + "="*60)
        print("❌ Knowledge Base Preparation Failed")
        print("="*60)
        print(f"Error: {summary.get('error', 'Unknown error')}")
        print("="*60 + "\n")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
