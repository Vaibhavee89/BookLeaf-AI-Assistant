# BookLeaf AI Assistant

An AI-powered customer support system for BookLeaf Publishing that intelligently handles customer queries across multiple channels with identity unification, RAG-based knowledge retrieval, and automatic escalation.

## 🌟 Features

- **Multi-Stage Identity Unification**: Accurately identifies customers across platforms using fuzzy matching and LLM-based disambiguation
- **RAG-Powered Responses**: Retrieves relevant information from company knowledge base using vector embeddings (Supabase pgvector)
- **Confidence-Based Routing**: Automatically escalates low-confidence queries (< 80%) to human agents
- **Intelligent Model Routing**: Uses GPT-5-turbo for complex queries, GPT-4o for standard, GPT-4o-mini for classification
- **Multi-Channel Ready**: Designed to integrate with Email, WhatsApp, Instagram, and Web Chat

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │  Next.js 14 + Tailwind + shadcn/ui
└──────┬──────┘
       │
       │ REST API
       │
┌──────▼──────┐
│   FastAPI   │  Python 3.11+ Backend
│   Backend   │
└──────┬──────┘
       │
       ├─────► Identity Matcher (Fuzzy + LLM)
       │
       ├─────► RAG System (pgvector + OpenAI embeddings)
       │
       ├─────► LLM Router (GPT-5-turbo / GPT-4o)
       │
       └─────► Supabase (PostgreSQL + pgvector)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account
- OpenAI API key

### Installation

1. **Clone and setup backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and Supabase credentials
   ```

3. **Setup database**:
   - Follow instructions in `docs/SUPABASE_SETUP.md`
   - Run: `python backend/scripts/seed_data.py`

4. **Generate knowledge base embeddings**:
   ```bash
   python backend/scripts/prepare_knowledge_base.py
   ```

5. **Start backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

6. **Setup and start frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

7. **Access the application**:
   - Frontend: http://localhost:3000/chat
   - API Documentation: http://localhost:8000/docs

## 📚 Documentation

- [Complete Setup Guide](docs/SETUP.md)
- [Supabase Configuration](docs/SUPABASE_SETUP.md)
- [API Documentation](docs/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Demo Script](docs/DEMO_SCRIPT.md)

## 🧪 Testing

```bash
cd backend
pytest tests/ -v --cov=app
```

## 🛠️ Tech Stack

**Backend**:
- FastAPI (REST API)
- OpenAI API (GPT-5-turbo, GPT-4o, GPT-4o-mini)
- Supabase (PostgreSQL + pgvector)
- RapidFuzz (Fuzzy matching)
- Pydantic (Data validation)

**Frontend**:
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components

**Database**:
- PostgreSQL 15+
- pgvector extension
- text-embedding-3-large (1536 dimensions)

## 📊 Key Capabilities

### Identity Matching Pipeline

1. **Exact Match**: Normalized email/phone lookup (100% confidence)
2. **Fuzzy Match**: RapidFuzz with 85% threshold (70-90% confidence)
3. **LLM Disambiguation**: GPT-4o-mini with context (50-90% confidence)
4. **New Identity**: Create if confidence < 50%

### Confidence Scoring

Weighted multi-factor calculation:
- Identity confidence: 30%
- Intent classification: 20%
- RAG retrieval relevance: 25%
- LLM self-assessment: 25%

**Threshold**: >80% auto-respond, <80% escalate to human

### Query Processing

1. Classify intent (author_specific, general_knowledge, technical_support, out_of_scope)
2. Extract entities (names, titles, dates, amounts)
3. Retrieve RAG context for knowledge queries
4. Query database for author-specific data
5. Generate response with LLM
6. Calculate confidence and route

## 🎯 Use Cases Demonstrated

- ✅ High confidence author-specific query (royalty payment status)
- ✅ Knowledge base retrieval (publishing process, royalty structure)
- ✅ Identity unification across platforms (fuzzy name matching)
- ✅ Low confidence escalation (ambiguous queries)
- ✅ Multi-channel readiness (webhook integration guides)

## 📦 Project Structure

```
BookLeaf_Assignment/
├── backend/              # Python FastAPI application
├── frontend/             # Next.js web interface
├── knowledge-base/       # RAG documents (markdown)
├── data/                 # Mock authors and test queries
├── docs/                 # Comprehensive documentation
├── database/             # SQL schema files
└── automation/           # n8n/Make.com integration guides
```

## 🔐 Security & Production Readiness

- API key management via environment variables
- Input validation with Pydantic schemas
- Rate limiting and retry logic
- Structured logging for debugging
- Error handling with graceful degradation
- CORS configuration for frontend
- SQL injection prevention (parameterized queries)

## 🚧 Future Enhancements

- Real-time notifications via Supabase Realtime
- Multi-channel integration (WhatsApp, Instagram, Email)
- Advanced analytics dashboard
- A/B testing for prompt optimization
- Fine-tuned models for domain-specific tasks
- Redis caching for frequently asked questions
- Admin UI for escalation queue management

## 📝 License

This is a demonstration project for BookLeaf Publishing.

## 👤 Author

Built as part of the BookLeaf Publishing AI Assistant assignment.

---

For detailed setup instructions, see [SETUP.md](docs/SETUP.md).
