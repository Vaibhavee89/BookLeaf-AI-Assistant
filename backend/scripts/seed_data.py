"""Seed script to populate database with mock authors and identities."""

import json
import sys
import os
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.db.client import supabase
import structlog

logger = structlog.get_logger(__name__)


def load_mock_authors():
    """Load mock authors from JSON file."""
    # Try Docker mount path first, then local path
    data_file_docker = Path("/data/authors_mock.json")
    data_file_local = Path(__file__).parent.parent.parent / "data" / "authors_mock.json"

    data_file = data_file_docker if data_file_docker.exists() else data_file_local

    with open(data_file, 'r') as f:
        authors = json.load(f)

    logger.info("loaded_mock_authors", count=len(authors))
    return authors


def create_author(author_data):
    """
    Create an author in the database.

    Args:
        author_data: Dictionary with author information

    Returns:
        Created author record
    """
    try:
        # Create author
        result = supabase.table("authors").insert({
            "full_name": author_data["full_name"],
            "email": author_data.get("email"),
            "phone": author_data.get("phone"),
            "metadata": author_data.get("metadata", {})
        }).execute()

        if not result.data:
            logger.error("author_creation_failed", author=author_data["full_name"])
            return None

        author = result.data[0]
        logger.info("author_created", author_id=author["id"], name=author["full_name"])

        return author

    except Exception as e:
        logger.error("author_creation_error", error=str(e), author=author_data["full_name"])
        return None


def create_identity(author_id, platform, identifier, confidence=1.0):
    """
    Create an identity for an author.

    Args:
        author_id: Author UUID
        platform: Platform name ('email', 'whatsapp', 'instagram', 'web_chat')
        identifier: Platform-specific identifier
        confidence: Confidence score (default 1.0 for seeded data)

    Returns:
        Created identity record
    """
    try:
        # Normalize identifier
        normalized = identifier.lower().strip() if identifier else None

        result = supabase.table("identities").insert({
            "author_id": author_id,
            "platform": platform,
            "platform_identifier": identifier,
            "normalized_identifier": normalized,
            "confidence_score": confidence,
            "matching_method": "exact",
            "matching_metadata": {"source": "seed_data"},
            "verified": True
        }).execute()

        if not result.data:
            logger.error("identity_creation_failed", author_id=author_id, platform=platform)
            return None

        identity = result.data[0]
        logger.info("identity_created", identity_id=identity["id"], platform=platform)

        return identity

    except Exception as e:
        logger.error("identity_creation_error", error=str(e), author_id=author_id, platform=platform)
        return None


def seed_authors_and_identities():
    """Main seeding function."""
    logger.info("seeding_started")

    # Load mock authors
    authors_data = load_mock_authors()

    created_count = 0
    identity_count = 0

    for author_data in authors_data:
        # Create author
        author = create_author(author_data)
        if not author:
            continue

        created_count += 1
        author_id = author["id"]

        # Create email identity
        if author_data.get("email"):
            identity = create_identity(author_id, "email", author_data["email"])
            if identity:
                identity_count += 1

        # Create phone/whatsapp identity
        if author_data.get("phone"):
            # Determine platform based on preferred_contact
            preferred = author_data.get("metadata", {}).get("preferred_contact", "phone")
            platform = "whatsapp" if preferred == "whatsapp" else "phone"

            identity = create_identity(author_id, platform, author_data["phone"])
            if identity:
                identity_count += 1

        # Create Instagram identity for some authors (use email username)
        if author_data.get("metadata", {}).get("preferred_contact") == "instagram":
            if author_data.get("email"):
                # Generate Instagram username from email
                username = author_data["email"].split("@")[0]
                instagram_handle = f"@{username}"

                identity = create_identity(author_id, "instagram", instagram_handle)
                if identity:
                    identity_count += 1

    logger.info(
        "seeding_completed",
        authors_created=created_count,
        identities_created=identity_count
    )

    print(f"\n{'='*60}")
    print(f"✅ Seeding completed successfully!")
    print(f"{'='*60}")
    print(f"Authors created: {created_count}")
    print(f"Identities created: {identity_count}")
    print(f"{'='*60}\n")


def clear_existing_data():
    """Clear existing data (for development/testing)."""
    try:
        logger.warning("clearing_existing_data")

        # Delete in reverse order of dependencies
        supabase.table("query_analytics").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase.table("escalations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase.table("messages").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase.table("conversations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase.table("identities").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase.table("authors").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

        logger.info("existing_data_cleared")
        print("✅ Existing data cleared\n")

    except Exception as e:
        logger.error("data_clearing_error", error=str(e))
        print(f"⚠️ Warning: Could not clear existing data: {e}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("BookLeaf AI Assistant - Database Seeding")
    print("="*60 + "\n")

    # Ask user if they want to clear existing data
    response = input("Do you want to clear existing data first? (y/N): ").strip().lower()
    if response == 'y':
        clear_existing_data()

    # Seed new data
    seed_authors_and_identities()

    print("You can now verify the data in your Supabase dashboard:")
    print("1. Go to Table Editor → authors")
    print("2. Go to Table Editor → identities")
    print("\nNext step: Run prepare_knowledge_base.py to generate embeddings\n")
