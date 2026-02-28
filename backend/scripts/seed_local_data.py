"""Seed script for local SQLite database with mock data."""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.db.local_client import local_db
import structlog

logger = structlog.get_logger(__name__)


# Mock authors data with book status
MOCK_AUTHORS = [
    {
        "full_name": "Sarah Johnson",
        "email": "sarah.johnson@email.com",
        "phone": "+1-555-0101",
        "metadata": {
            "preferred_contact": "email",
            "books": [
                {
                    "title": "The Midnight Garden",
                    "status": "live",
                    "published_date": "2025-01-15",
                    "isbn": "978-1-234567-89-0"
                }
            ],
            "royalty": {
                "next_payment_date": "2026-03-15",
                "amount": "$2,450.00",
                "period": "Q1 2026"
            },
            "author_copy": {
                "status": "shipped",
                "tracking_number": "1Z999AA10123456784",
                "shipped_date": "2026-02-20"
            }
        }
    },
    {
        "full_name": "Michael Chen",
        "email": "m.chen@author.com",
        "phone": "+1-555-0102",
        "metadata": {
            "preferred_contact": "whatsapp",
            "books": [
                {
                    "title": "Code & Coffee",
                    "status": "in_review",
                    "expected_date": "2026-03-30",
                    "submission_date": "2026-02-10"
                }
            ],
            "royalty": {
                "next_payment_date": "2026-04-15",
                "amount": "pending",
                "period": "Q1 2026"
            },
            "author_copy": {
                "status": "pending",
                "expected_date": "2026-04-05"
            }
        }
    },
    {
        "full_name": "Emma Rodriguez",
        "email": "emma.r@bookmail.com",
        "phone": "+1-555-0103",
        "metadata": {
            "preferred_contact": "email",
            "books": [
                {
                    "title": "Whispers in the Wind",
                    "status": "live",
                    "published_date": "2024-09-20",
                    "isbn": "978-1-234567-90-6"
                },
                {
                    "title": "Beyond the Horizon",
                    "status": "in_production",
                    "expected_date": "2026-04-15"
                }
            ],
            "royalty": {
                "next_payment_date": "2026-03-15",
                "amount": "$3,890.00",
                "period": "Q1 2026"
            },
            "author_copy": {
                "status": "delivered",
                "delivered_date": "2024-10-05",
                "copies": 10
            }
        }
    },
    {
        "full_name": "James Williams",
        "email": "jwilliams@writers.net",
        "phone": "+1-555-0104",
        "metadata": {
            "preferred_contact": "phone",
            "books": [
                {
                    "title": "The Last Frontier",
                    "status": "submitted",
                    "submission_date": "2026-02-25",
                    "expected_review_date": "2026-03-25"
                }
            ],
            "royalty": {
                "next_payment_date": "N/A",
                "amount": "N/A",
                "period": "N/A"
            },
            "author_copy": {
                "status": "not_applicable",
                "note": "Will be available after publication"
            }
        }
    },
    {
        "full_name": "Priya Sharma",
        "email": "priya.sharma@gmail.com",
        "phone": "+91-9876543210",
        "metadata": {
            "preferred_contact": "whatsapp",
            "books": [
                {
                    "title": "Monsoon Memories",
                    "status": "live",
                    "published_date": "2025-06-10",
                    "isbn": "978-1-234567-91-3"
                }
            ],
            "royalty": {
                "next_payment_date": "2026-03-15",
                "amount": "$1,850.00",
                "period": "Q4 2025 & Q1 2026"
            },
            "author_copy": {
                "status": "in_transit",
                "tracking_number": "IN123456789",
                "expected_delivery": "2026-03-05"
            }
        }
    },
    {
        "full_name": "Robert Brown",
        "email": "rbrown@authorhouse.com",
        "phone": "+1-555-0105",
        "metadata": {
            "preferred_contact": "email",
            "books": [
                {
                    "title": "Tech Titans",
                    "status": "live",
                    "published_date": "2023-11-15",
                    "isbn": "978-1-234567-92-0"
                }
            ],
            "royalty": {
                "next_payment_date": "2026-03-15",
                "amount": "$5,200.00",
                "period": "Q4 2025 & Q1 2026",
                "bestseller": True
            },
            "author_copy": {
                "status": "delivered",
                "delivered_date": "2023-12-01",
                "copies": 25
            }
        }
    },
    {
        "full_name": "Aisha Mohamed",
        "email": "aisha.m@stories.com",
        "phone": "+971-50-1234567",
        "metadata": {
            "preferred_contact": "instagram",
            "books": [
                {
                    "title": "Desert Dreams",
                    "status": "in_editing",
                    "expected_date": "2026-05-20",
                    "submission_date": "2026-01-15"
                }
            ],
            "royalty": {
                "next_payment_date": "N/A",
                "amount": "N/A",
                "period": "N/A"
            },
            "author_copy": {
                "status": "not_yet",
                "note": "Available after publication"
            }
        }
    },
    {
        "full_name": "David Martinez",
        "email": "dmartinez@books.org",
        "phone": "+1-555-0106",
        "metadata": {
            "preferred_contact": "email",
            "books": [
                {
                    "title": "The Algorithm",
                    "status": "live",
                    "published_date": "2024-03-01",
                    "isbn": "978-1-234567-93-7"
                }
            ],
            "royalty": {
                "next_payment_date": "2026-03-15",
                "amount": "$2,980.00",
                "period": "Q4 2025 & Q1 2026"
            },
            "author_copy": {
                "status": "shipped",
                "tracking_number": "1Z999AA10987654321",
                "shipped_date": "2026-02-18"
            }
        }
    },
    {
        "full_name": "Lisa Anderson",
        "email": "l.anderson@writemail.com",
        "phone": "+1-555-0107",
        "metadata": {
            "preferred_contact": "phone",
            "books": [
                {
                    "title": "Healing Hearts",
                    "status": "live",
                    "published_date": "2025-08-20",
                    "isbn": "978-1-234567-94-4"
                }
            ],
            "royalty": {
                "next_payment_date": "2026-03-15",
                "amount": "$3,120.00",
                "period": "Q4 2025 & Q1 2026"
            },
            "author_copy": {
                "status": "delivered",
                "delivered_date": "2025-09-10",
                "copies": 15
            }
        }
    },
    {
        "full_name": "Kenji Tanaka",
        "email": "k.tanaka@novelists.jp",
        "phone": "+81-90-1234-5678",
        "metadata": {
            "preferred_contact": "email",
            "books": [
                {
                    "title": "Tokyo Nights",
                    "status": "submitted",
                    "submission_date": "2026-02-28",
                    "expected_review_date": "2026-03-30"
                }
            ],
            "royalty": {
                "next_payment_date": "N/A",
                "amount": "N/A",
                "period": "N/A"
            },
            "author_copy": {
                "status": "pending",
                "note": "Will ship after publication approval"
            }
        }
    },
    {
        "full_name": "Maria Garcia",
        "email": "mgarcia@authors.es",
        "phone": "+34-612-345-678",
        "metadata": {
            "preferred_contact": "whatsapp",
            "books": [
                {
                    "title": "Flamenco Fire",
                    "status": "live",
                    "published_date": "2024-12-10",
                    "isbn": "978-1-234567-95-1"
                }
            ],
            "royalty": {
                "next_payment_date": "2026-03-15",
                "amount": "$2,650.00",
                "period": "Q4 2025 & Q1 2026"
            },
            "author_copy": {
                "status": "delivered",
                "delivered_date": "2025-01-08",
                "copies": 12
            }
        }
    },
    {
        "full_name": "Thomas Wright",
        "email": "twright@penandpaper.com",
        "phone": "+44-7700-900123",
        "metadata": {
            "preferred_contact": "email",
            "books": [
                {
                    "title": "The London Fog Mysteries",
                    "status": "in_production",
                    "expected_date": "2026-04-10",
                    "submission_date": "2025-12-01"
                }
            ],
            "royalty": {
                "next_payment_date": "N/A",
                "amount": "N/A",
                "period": "Will be available after publication"
            },
            "author_copy": {
                "status": "production",
                "expected_date": "2026-04-20"
            }
        }
    },
    {
        "full_name": "Sophie Laurent",
        "email": "s.laurent@ecrivains.fr",
        "phone": "+33-6-12-34-56-78",
        "metadata": {
            "preferred_contact": "email",
            "books": [
                {
                    "title": "Parisian Nights",
                    "status": "live",
                    "published_date": "2025-05-15",
                    "isbn": "978-1-234567-96-8"
                }
            ],
            "royalty": {
                "next_payment_date": "2026-03-15",
                "amount": "€2,890.00",
                "period": "Q4 2025 & Q1 2026"
            },
            "author_copy": {
                "status": "delivered",
                "delivered_date": "2025-06-20",
                "copies": 10
            }
        }
    },
    {
        "full_name": "Carlos Silva",
        "email": "csilva@livros.br",
        "phone": "+55-11-98765-4321",
        "metadata": {
            "preferred_contact": "whatsapp",
            "books": [
                {
                    "title": "Amazon Legends",
                    "status": "in_review",
                    "expected_date": "2026-04-05",
                    "submission_date": "2026-01-20"
                }
            ],
            "royalty": {
                "next_payment_date": "N/A",
                "amount": "N/A",
                "period": "N/A"
            },
            "author_copy": {
                "status": "pending",
                "expected_date": "2026-04-15"
            }
        }
    },
    {
        "full_name": "Anna Kowalski",
        "email": "akowalski@writers.pl",
        "phone": "+48-501-234-567",
        "metadata": {
            "preferred_contact": "email",
            "books": [
                {
                    "title": "Warsaw Stories",
                    "status": "live",
                    "published_date": "2025-10-01",
                    "isbn": "978-1-234567-97-5"
                }
            ],
            "royalty": {
                "next_payment_date": "2026-03-15",
                "amount": "$1,940.00",
                "period": "Q4 2025 & Q1 2026"
            },
            "author_copy": {
                "status": "delivered",
                "delivered_date": "2025-11-05",
                "copies": 8
            }
        }
    },
    {
        "full_name": "Ahmed Hassan",
        "email": "ahassang@authors.eg",
        "phone": "+20-10-1234-5678",
        "metadata": {
            "preferred_contact": "whatsapp",
            "books": [
                {
                    "title": "Nile Chronicles",
                    "status": "in_editing",
                    "expected_date": "2026-05-15",
                    "submission_date": "2026-01-10"
                }
            ],
            "royalty": {
                "next_payment_date": "N/A",
                "amount": "N/A",
                "period": "N/A"
            },
            "author_copy": {
                "status": "not_yet",
                "note": "Available after publication"
            }
        }
    },
    {
        "full_name": "Jennifer Lee",
        "email": "jlee@bookauthors.com",
        "phone": "+1-555-0108",
        "metadata": {
            "preferred_contact": "email",
            "books": [
                {
                    "title": "Silicon Valley Dreams",
                    "status": "live",
                    "published_date": "2024-07-20",
                    "isbn": "978-1-234567-98-2"
                }
            ],
            "royalty": {
                "next_payment_date": "2026-03-15",
                "amount": "$4,320.00",
                "period": "Q4 2025 & Q1 2026",
                "bestseller": True
            },
            "author_copy": {
                "status": "delivered",
                "delivered_date": "2024-08-15",
                "copies": 20
            }
        }
    },
    {
        "full_name": "Hans Mueller",
        "email": "hmueller@autoren.de",
        "phone": "+49-171-1234567",
        "metadata": {
            "preferred_contact": "email",
            "books": [
                {
                    "title": "Berlin Walls",
                    "status": "submitted",
                    "submission_date": "2026-02-20",
                    "expected_review_date": "2026-03-20"
                }
            ],
            "royalty": {
                "next_payment_date": "N/A",
                "amount": "N/A",
                "period": "N/A"
            },
            "author_copy": {
                "status": "pending",
                "note": "Will ship after approval"
            }
        }
    },
    {
        "full_name": "Fatima Al-Rashid",
        "email": "falrashid@books.sa",
        "phone": "+966-50-123-4567",
        "metadata": {
            "preferred_contact": "whatsapp",
            "books": [
                {
                    "title": "Desert Rose",
                    "status": "live",
                    "published_date": "2025-11-05",
                    "isbn": "978-1-234567-99-9"
                }
            ],
            "royalty": {
                "next_payment_date": "2026-03-15",
                "amount": "$2,150.00",
                "period": "Q4 2025 & Q1 2026"
            },
            "author_copy": {
                "status": "in_transit",
                "tracking_number": "SA987654321",
                "expected_delivery": "2026-03-10"
            }
        }
    },
    {
        "full_name": "Daniel O'Brien",
        "email": "dobrien@irishwriters.ie",
        "phone": "+353-87-123-4567",
        "metadata": {
            "preferred_contact": "email",
            "books": [
                {
                    "title": "Dublin Tales",
                    "status": "in_production",
                    "expected_date": "2026-04-25",
                    "submission_date": "2025-11-15"
                }
            ],
            "royalty": {
                "next_payment_date": "N/A",
                "amount": "N/A",
                "period": "Will be available after publication"
            },
            "author_copy": {
                "status": "production",
                "expected_date": "2026-05-05"
            }
        }
    }
]


def create_author(author_data):
    """Create an author in the local database."""
    try:
        result = local_db.table("authors").insert({
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
    """Create an identity for an author."""
    try:
        normalized = identifier.lower().strip() if identifier else None

        result = local_db.table("identities").insert({
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
    """Seed authors and identities into local database."""
    logger.info("seeding_started")

    created_count = 0
    identity_count = 0

    for author_data in MOCK_AUTHORS:
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
            preferred = author_data.get("metadata", {}).get("preferred_contact", "phone")
            platform = "whatsapp" if preferred == "whatsapp" else "phone"

            identity = create_identity(author_id, platform, author_data["phone"])
            if identity:
                identity_count += 1

        # Create Instagram identity for some authors
        if author_data.get("metadata", {}).get("preferred_contact") == "instagram":
            if author_data.get("email"):
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
    print(f"✅ Local database seeding completed successfully!")
    print(f"{'='*60}")
    print(f"Authors created: {created_count}")
    print(f"Identities created: {identity_count}")
    print(f"{'='*60}\n")


def clear_existing_data():
    """Clear existing data from local database."""
    try:
        logger.warning("clearing_existing_data")

        # Delete in reverse order of dependencies
        local_db.table("query_analytics").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        local_db.table("escalations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        local_db.table("messages").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        local_db.table("conversations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        local_db.table("identities").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        local_db.table("authors").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

        logger.info("existing_data_cleared")
        print("✅ Existing data cleared\n")

    except Exception as e:
        logger.error("data_clearing_error", error=str(e))
        print(f"⚠️  Warning: Could not clear existing data: {e}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("BookLeaf AI Assistant - Local Database Seeding")
    print("="*60 + "\n")

    # Ask user if they want to clear existing data
    response = input("Do you want to clear existing data first? (y/N): ").strip().lower()
    if response == 'y':
        clear_existing_data()

    # Seed new data
    seed_authors_and_identities()

    print("You can now start the backend and test the chat interface with local storage!")
    print("The system will use SQLite database instead of Supabase.\n")
