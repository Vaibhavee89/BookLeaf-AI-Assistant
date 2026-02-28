"""Script to prepare knowledge base for local database (without vector embeddings)."""

import sys
import os
from pathlib import Path
import re

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.db.local_client import local_db
import structlog

logger = structlog.get_logger(__name__)


class LocalKnowledgeBasePreparator:
    """Service to prepare knowledge base documents for local storage."""

    def __init__(self):
        """Initialize the preparator."""
        self.knowledge_base_dir = Path(__file__).parent.parent.parent / "knowledge-base"
        self.chunk_size = 500  # characters

        logger.info(
            "preparator_initialized",
            knowledge_base_dir=str(self.knowledge_base_dir)
        )

    def load_document(self, file_path: Path):
        """Load a markdown document from file."""
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

    def chunk_document(self, content: str):
        """Chunk document into overlapping pieces."""
        chunks = []
        chunk_index = 0
        chunk_overlap = 50  # characters

        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        current_chunk = ""

        for para in paragraphs:
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append({
                    "chunk_index": chunk_index,
                    "chunk_text": current_chunk.strip(),
                    "metadata": {
                        "position": f"{chunk_index + 1}"
                    }
                })
                chunk_index += 1

                # Start new chunk with overlap (last few words)
                words = current_chunk.split()
                overlap_words = words[-10:] if len(words) > 10 else words
                current_chunk = ' '.join(overlap_words) + '\n\n' + para
            else:
                current_chunk += '\n\n' + para if current_chunk else para

        # Add remaining content as last chunk
        if current_chunk.strip():
            chunks.append({
                "chunk_index": chunk_index,
                "chunk_text": current_chunk.strip(),
                "metadata": {
                    "position": f"{chunk_index + 1}"
                }
            })

        logger.info(
            "chunking_completed",
            total_chunks=len(chunks)
        )

        return chunks

    def store_document(self, document):
        """Store document in knowledge_documents table."""
        try:
            result = local_db.table("knowledge_documents").insert({
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

    def store_chunks(self, document_id: str, chunks):
        """Store chunks in knowledge_embeddings table (without actual embeddings)."""
        stored_count = 0

        for chunk in chunks:
            try:
                result = local_db.table("knowledge_embeddings").insert({
                    "document_id": document_id,
                    "chunk_text": chunk["chunk_text"],
                    "chunk_index": chunk["chunk_index"],
                    "embedding": "[]",  # Empty embedding for local storage
                    "metadata": chunk["metadata"]
                }).execute()

                if result.data:
                    stored_count += 1

            except Exception as e:
                logger.error(
                    "chunk_storage_failed",
                    chunk_index=chunk["chunk_index"],
                    error=str(e)
                )
                continue

        logger.info(
            "chunks_stored",
            document_id=document_id,
            stored_count=stored_count,
            total_chunks=len(chunks)
        )

        return stored_count

    def process_document(self, file_path: Path):
        """Process a single document: load, chunk, and store."""
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

        # Store chunks
        stored_count = self.store_chunks(document_id, chunks)

        result = {
            "success": True,
            "document_id": document_id,
            "title": document["title"],
            "total_chunks": len(chunks),
            "chunks_stored": stored_count
        }

        logger.info("document_processing_completed", **result)

        return result

    def process_all_documents(self):
        """Process all markdown documents in knowledge base directory."""
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

        for md_file in md_files:
            result = self.process_document(md_file)
            results.append(result)

            if result["success"]:
                total_chunks += result["total_chunks"]

        summary = {
            "success": True,
            "documents_processed": len(results),
            "documents_successful": sum(1 for r in results if r["success"]),
            "total_chunks": total_chunks,
            "results": results
        }

        logger.info("knowledge_base_processing_completed", **{
            k: v for k, v in summary.items() if k != "results"
        })

        return summary

    def clear_existing_data(self):
        """Clear existing knowledge base data."""
        try:
            logger.warning("clearing_existing_knowledge_base")

            local_db.table("knowledge_embeddings").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            local_db.table("knowledge_documents").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

            logger.info("existing_knowledge_base_cleared")
            print("✅ Existing knowledge base data cleared\n")

        except Exception as e:
            logger.error("data_clearing_error", error=str(e))
            print(f"⚠️  Warning: Could not clear existing data: {e}\n")


def main():
    """Main function to run knowledge base preparation."""
    print("\n" + "="*60)
    print("BookLeaf AI Assistant - Local Knowledge Base Preparation")
    print("="*60 + "\n")

    preparator = LocalKnowledgeBasePreparator()

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
        print("="*60 + "\n")

        print("Document details:")
        for result in summary["results"]:
            if result["success"]:
                print(f"  ✓ {result['title']}: {result['chunks_stored']} chunks")
            else:
                print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")

        print("\nKnowledge base is ready for local text search!")
        print("Note: Vector similarity search is not available in local mode.")
        print("The system will use keyword-based matching instead.\n")

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
