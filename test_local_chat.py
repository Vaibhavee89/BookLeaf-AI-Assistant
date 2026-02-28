"""Test script for local chat system."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.core.query.local_processor import local_query_processor
from app.db.local_client import local_db


def test_queries():
    """Test various queries."""

    print("\n" + "=" * 70)
    print("BookLeaf AI Assistant - Local Mode Test")
    print("=" * 70 + "\n")

    # Get a sample author
    authors_result = local_db.table("authors").select("*").execute()
    if not authors_result.data:
        print("❌ No authors found in database. Please run seed_local_data.py first.")
        return

    sample_author = authors_result.data[0]
    print(f"Testing with author: {sample_author['full_name']}")
    print(f"Email: {sample_author.get('email', 'N/A')}\n")

    # Test queries
    test_cases = [
        {
            "query": "Hello!",
            "identity": {"author_id": sample_author["id"]},
            "description": "Greeting"
        },
        {
            "query": "Is my book live yet?",
            "identity": {"author_id": sample_author["id"]},
            "description": "Book status inquiry"
        },
        {
            "query": "When will I get my royalty?",
            "identity": {"author_id": sample_author["id"]},
            "description": "Royalty payment inquiry"
        },
        {
            "query": "Where's my author copy?",
            "identity": {"author_id": sample_author["id"]},
            "description": "Author copy inquiry"
        },
        {
            "query": "What is your refund policy?",
            "identity": None,
            "description": "General knowledge query"
        },
        {
            "query": "How do I access my dashboard?",
            "identity": None,
            "description": "Dashboard help"
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {i}: {test['description']}")
        print(f"{'='*70}")
        print(f"Query: \"{test['query']}\"\n")

        # Process query
        result = local_query_processor.process_query(
            query=test["query"],
            identity_info=test["identity"]
        )

        # Display results
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Action: {result['action']}")
        print(f"\nResponse:")
        print("-" * 70)
        print(result["answer"])
        print("-" * 70)

    print(f"\n{'='*70}")
    print("✅ All tests completed successfully!")
    print(f"{'='*70}\n")


def test_knowledge_base():
    """Test knowledge base retrieval."""
    from app.core.rag.local_retriever import local_rag_retriever

    print("\n" + "=" * 70)
    print("Knowledge Base Test")
    print("=" * 70 + "\n")

    queries = [
        "royalty payment schedule",
        "how to publish a book",
        "premium services available",
        "author dashboard features"
    ]

    for query in queries:
        print(f"\nQuery: \"{query}\"")
        print("-" * 70)

        chunks = local_rag_retriever.retrieve(query, top_k=3)

        if chunks:
            print(f"Found {len(chunks)} relevant chunks:\n")
            for j, chunk in enumerate(chunks, 1):
                print(f"{j}. From '{chunk['document_title']}' (score: {chunk['score']})")
                print(f"   {chunk['chunk_text'][:150]}...\n")
        else:
            print("No relevant chunks found.\n")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        # Test knowledge base
        test_knowledge_base()

        # Test query processing
        test_queries()

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
