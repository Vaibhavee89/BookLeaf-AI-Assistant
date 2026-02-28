# BookLeaf AI Assistant - Local Mode

A multi-channel-ready query responder that works **completely offline** with local SQLite database. No Supabase or OpenAI API required!

## Features

✅ **Multi-channel ready**: Supports Email, WhatsApp, Instagram, Web Chat
✅ **Identity matching**: Fuzzy matching of authors across platforms
✅ **Smart query processing**: Intent classification and entity extraction
✅ **Knowledge base**: 4 comprehensive documents with 116 searchable chunks
✅ **Mock data**: 20 realistic authors with books, royalties, and shipment data
✅ **Confidence scoring**: Automatic escalation for low-confidence queries
✅ **Local-first**: Works completely offline with SQLite

## Quick Start

### 1. Setup (One-time)

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pydantic structlog python-dotenv

# Seed local database with 20 mock authors
python3 scripts/seed_local_data.py

# Load knowledge base (4 documents, 116 chunks)
python3 scripts/prepare_local_knowledge_base.py
```

### 2. Start the API Server

```bash
cd backend
source venv/bin/activate

# Start local API server
python3 -m uvicorn app.main_local:app --host 0.0.0.0 --port 8000
```

The server will start at: **http://localhost:8000**

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 3. Test the System

#### Option A: Command Line Test

```bash
# Run test script
cd backend
source venv/bin/activate
cd ..
python3 test_local_chat.py
```

#### Option B: cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Simple query without identity
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is your refund policy?"
  }'

# Query with author identity (Sarah Johnson)
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Is my book live yet?",
    "identity": {
      "name": "Sarah Johnson",
      "email": "sarah.johnson@email.com",
      "platform": "web_chat"
    }
  }'

# Royalty inquiry
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "When will I get my royalty?",
    "identity": {
      "name": "Sarah Johnson",
      "email": "sarah.johnson@email.com",
      "platform": "email"
    }
  }'

# Author copy tracking
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Where is my author copy?",
    "identity": {
      "name": "Michael Chen",
      "email": "m.chen@author.com",
      "platform": "whatsapp"
    }
  }'
```

#### Option C: Web Interface

Open `test_chat.html` in your browser for a simple chat interface.

## Query Examples

The system can handle:

### Book Status Queries
- "Is my book live yet?"
- "When will my book be published?"
- "What's the status of my manuscript?"

### Royalty Inquiries
- "When will I get my royalty?"
- "How much will I earn?"
- "When is my next payment?"

### Author Copy Tracking
- "Where's my author copy?"
- "Has my book been shipped?"
- "What's my tracking number?"

### Knowledge Base Queries
- "What is your refund policy?"
- "How do I publish a book?"
- "What premium services are available?"
- "How do I access my dashboard?"
- "What are the royalty rates?"

## Mock Authors

The system includes 20 mock authors with realistic data:

1. **Sarah Johnson** - Book live, royalty scheduled, copy shipped
2. **Michael Chen** - Book in review, copy pending
3. **Emma Rodriguez** - Multiple books, bestseller status
4. **James Williams** - Recently submitted manuscript
5. **Priya Sharma** - Book live, copy in transit
... and 15 more!

Each author has:
- Full name, email, phone
- Book status (live, in_review, in_production, etc.)
- Royalty payment schedule and amounts
- Author copy shipping status with tracking

## Knowledge Base

4 comprehensive documents covering:

1. **Publishing Process** (18 chunks)
   - Manuscript submission to publication
   - Review stages and timelines
   - Quality assurance

2. **Royalty Structure** (25 chunks)
   - Payment terms and schedules
   - Royalty percentages by format
   - Returns and adjustments

3. **Author Dashboard** (35 chunks)
   - Dashboard features and navigation
   - Sales reporting
   - Profile management

4. **Premium Add-ons** (38 chunks)
   - Professional editing services
   - Marketing packages
   - Audio book production

## Architecture

```
Local SQLite Database
├── authors (20 entries)
├── identities (41 entries - email, phone, whatsapp, instagram)
├── conversations (chat history)
├── messages (user and assistant messages)
├── knowledge_documents (4 documents)
├── knowledge_embeddings (116 chunks - text search, no vectors)
├── escalations (low-confidence queries)
└── query_analytics (performance metrics)
```

### Intent Classification

Uses pattern matching to identify:
- `book_status` - Book publication queries
- `royalty_inquiry` - Payment and earnings
- `author_copy` - Shipment tracking
- `general_knowledge` - Knowledge base queries
- `greeting` - Hello, hi, etc.

### Confidence Scoring

- **0.90-0.95**: Author-specific queries with identity match
- **0.85**: Knowledge base queries with matches
- **0.70**: Queries needing identity clarification
- **<0.80**: Automatically escalated to human agent

### Knowledge Retrieval

- **Keyword extraction**: Removes stop words, extracts key terms
- **Text matching**: Scores chunks based on keyword frequency
- **Context building**: Assembles relevant chunks with source attribution
- **No vector embeddings**: Uses simple but effective text search

## API Endpoints

### POST /api/v1/chat/message
Send a chat message and get AI response.

**Request:**
```json
{
  "message": "Is my book live yet?",
  "identity": {
    "name": "Sarah Johnson",
    "email": "sarah.johnson@email.com",
    "platform": "email"
  },
  "conversation_id": "optional-uuid"
}
```

**Response:**
```json
{
  "response": "Great news! Your book 'The Midnight Garden' is live...",
  "confidence": 0.90,
  "intent": "book_status",
  "action": "respond",
  "conversation_id": "uuid",
  "metadata": {
    "has_identity": true,
    "author_name": "Sarah Johnson",
    "processing_method": "local"
  }
}
```

### GET /api/v1/chat/conversation/{id}
Get conversation history.

### GET /api/v1/health
Health check and status.

## Files Structure

```
backend/
├── app/
│   ├── main_local.py              # Local FastAPI app (no Supabase/OpenAI)
│   ├── api/v1/
│   │   └── local_chat.py          # Chat endpoints
│   ├── core/
│   │   ├── query/
│   │   │   └── local_processor.py # Query processing logic
│   │   └── rag/
│   │       └── local_retriever.py # Knowledge base retrieval
│   └── db/
│       ├── local_client.py        # SQLite database client
│       └── client.py              # Auto-fallback to local DB
├── scripts/
│   ├── seed_local_data.py         # Seed authors and identities
│   └── prepare_local_knowledge_base.py  # Load knowledge base
└── local_data/
    └── bookleaf.db                # SQLite database file

test_local_chat.py                 # Test script
test_chat.html                     # Simple web interface
```

## Benefits of Local Mode

1. **No API Keys Required**: Works without Supabase or OpenAI
2. **Zero Cost**: No per-query charges or API usage fees
3. **Fast Response**: No network latency for database/AI calls
4. **Privacy**: All data stays local
5. **Offline Capable**: Works without internet connection
6. **Easy Development**: Simple setup and debugging

## Limitations

- No vector similarity search (uses keyword matching instead)
- No LLM-powered responses (uses pattern matching + knowledge base)
- Simplified identity matching (exact and fuzzy only, no LLM disambiguation)

## Next Steps

### For Production

To move to production with full features:

1. **Connect to Supabase**: Update `.env` with Supabase credentials
2. **Add OpenAI API**: Set `OPENAI_API_KEY` for LLM responses
3. **Enable Vector Search**: Run `prepare_knowledge_base.py` to generate embeddings
4. **Use Full Pipeline**: Switch from `main_local.py` to `main.py`

### For Multi-Channel Integration

The system is ready for:

- **Email**: Use email-to-webhook service (SendGrid, Mailgun)
- **WhatsApp**: Integrate with Twilio or WhatsApp Business API
- **Instagram**: Use Instagram Graph API for DMs
- **Web Chat**: Already supported with current API

See `docs/INTEGRATION.md` for detailed multi-channel setup guides.

## Troubleshooting

### Database Issues

```bash
# Reset database
rm -rf local_data/
python3 backend/scripts/seed_local_data.py
python3 backend/scripts/prepare_local_knowledge_base.py
```

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Use different port
python3 -m uvicorn app.main_local:app --host 0.0.0.0 --port 8001
```

### Module Not Found

```bash
# Reinstall dependencies
cd backend
source venv/bin/activate
pip install --upgrade fastapi uvicorn pydantic structlog python-dotenv
```

## Demo

Watch the full demo video: [Loom Link Coming Soon]

## License

MIT License - Feel free to use and modify for your needs.

## Support

For questions or issues:
- GitHub Issues: [repository link]
- Email: support@bookleaf.com
- Documentation: See `docs/` folder

---

Built with ❤️ by the BookLeaf team
