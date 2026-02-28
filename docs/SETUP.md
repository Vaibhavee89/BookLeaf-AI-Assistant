# Complete Setup Guide

This guide walks you through setting up the complete BookLeaf AI Assistant system from scratch.

## Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **Supabase**: Account (free tier works)
- **OpenAI**: API key with GPT-4 access
- **Git**: For version control
- **Terminal**: Command line access

## Quick Start (15 minutes)

### 1. Clone or Download Project

```bash
cd /path/to/BookLeaf_Assignment
```

### 2. Set Up Supabase

Follow the detailed guide: [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)

**Quick steps**:
1. Create project at supabase.com
2. Enable `pgvector` extension
3. Run `database/schema.sql` in SQL Editor
4. Copy Project URL, anon key, and service_role key

### 3. Configure Backend

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Optional (has defaults)
PRIMARY_MODEL=gpt-4-turbo-preview
FALLBACK_MODEL=gpt-4
CLASSIFICATION_MODEL=gpt-4o-mini
```

### 4. Install Backend Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Seed Database

```bash
# From backend directory with venv activated
python scripts/seed_data.py
```

When prompted, type `y` to clear existing data (if any).

**Expected output**:
```
✅ Seeding completed successfully!
Authors created: 20
Identities created: 40+
```

### 6. Generate Knowledge Base Embeddings

```bash
python scripts/prepare_knowledge_base.py
```

When prompted, type `n` (don't clear existing data).

**Expected output**:
```
✅ Knowledge Base Preparation Completed!
Documents processed: 4
Total embeddings: 50-100
```

### 7. Start Backend

```bash
uvicorn app.main:app --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Test it**: Open http://localhost:8000/docs in browser

### 8. Configure Frontend

```bash
# In a new terminal
cd frontend
cp .env.local.example .env.local
```

Edit `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 9. Install Frontend Dependencies

```bash
npm install
```

### 10. Start Frontend

```bash
npm run dev
```

**Expected output**:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
```

### 11. Test the System

1. Open http://localhost:3000/chat
2. Fill in identity form:
   - Name: Sarah Johnson
   - Email: sarah.johnson@email.com
3. Click "Start Chatting"
4. Ask: "When will my royalty payment be processed?"
5. You should receive a response with confidence score

## Detailed Setup

### Backend Setup

#### Virtual Environment

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**:
```cmd
python -m venv venv
venv\Scripts\activate
```

To deactivate:
```bash
deactivate
```

#### Requirements Installation

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If you encounter issues:
```bash
pip install --no-cache-dir -r requirements.txt
```

#### Environment Variables

All configuration is in `backend/.env`. Key variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Service role key |
| `PRIMARY_MODEL` | No | Default: gpt-4-turbo-preview |
| `CONFIDENCE_THRESHOLD_AUTO_RESPOND` | No | Default: 0.80 |
| `RAG_TOP_K` | No | Default: 5 |

#### Running Tests

```bash
cd backend
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ -v --cov=app
```

### Frontend Setup

#### Dependencies

```bash
cd frontend
npm install
```

If you encounter peer dependency issues:
```bash
npm install --legacy-peer-deps
```

#### Environment Variables

Edit `frontend/.env.local`:

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL |
| `NEXT_PUBLIC_APP_NAME` | No | App name for branding |

#### Development Server

```bash
npm run dev
```

Options:
- Custom port: `npm run dev -- -p 3001`
- Turbopack: `npm run dev -- --turbo`

#### Production Build

```bash
npm run build
npm start
```

### Database Setup

See [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for complete guide.

**Quick checklist**:
- [ ] Supabase project created
- [ ] pgvector extension enabled
- [ ] Schema SQL executed
- [ ] All 8 tables created
- [ ] Test query successful

**Verify tables**:
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

Should show:
- authors
- conversations
- escalations
- identities
- knowledge_documents
- knowledge_embeddings
- messages
- query_analytics

## Verification

### Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

### Database Connection

```bash
cd backend
python -c "from app.db.client import supabase; print(supabase.table('authors').select('*').limit(1).execute())"
```

Should return author data without errors.

### API Endpoints

```bash
# Send a test message
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what are your royalty rates?",
    "name": "Test User",
    "email": "test@example.com"
  }'
```

Should return JSON with response and confidence score.

### Frontend

1. Navigate to http://localhost:3000/chat
2. Should see identity form
3. Fill in and submit
4. Should see chat interface
5. Send a message
6. Should receive response with confidence indicator

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError`

**Solution**:
```bash
pip install -r requirements.txt
# Ensure venv is activated
```

**Problem**: `openai.AuthenticationError`

**Solution**:
- Verify `OPENAI_API_KEY` in `.env`
- Check key is valid at platform.openai.com

**Problem**: `SupabaseError`

**Solution**:
- Verify Supabase credentials in `.env`
- Check project is active at supabase.com
- Ensure schema is created

**Problem**: `ImportError: No module named 'app'`

**Solution**:
```bash
# Make sure you're in backend directory
cd backend
# Run with module syntax
python -m pytest tests/
```

### Frontend Issues

**Problem**: `ECONNREFUSED` when sending messages

**Solution**:
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS is enabled in backend

**Problem**: Module not found errors

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

**Problem**: Build fails with type errors

**Solution**:
```bash
npm run type-check
# Fix reported errors
```

### Database Issues

**Problem**: "relation does not exist"

**Solution**:
- Run `database/schema.sql` in Supabase SQL Editor
- Verify all tables created

**Problem**: Slow vector queries

**Solution**:
```sql
-- Rebuild vector index
DROP INDEX IF EXISTS idx_knowledge_embeddings_vector;
CREATE INDEX idx_knowledge_embeddings_vector ON knowledge_embeddings
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
```

**Problem**: No embeddings found

**Solution**:
```bash
cd backend
python scripts/prepare_knowledge_base.py
# Type 'y' to clear and regenerate
```

## Performance Tuning

### Backend

1. **Increase workers**:
   ```bash
   uvicorn app.main:app --workers 4
   ```

2. **Use Gunicorn** (production):
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Optimize OpenAI calls**:
   - Set lower temperature (0.3) for consistency
   - Use streaming responses (not implemented yet)

### Frontend

1. **Production build**:
   ```bash
   npm run build
   NODE_ENV=production npm start
   ```

2. **Enable compression**:
   - Next.js handles this automatically

3. **Optimize images**:
   - Use Next.js Image component

### Database

1. **Add connection pooling** (Supabase handles this)

2. **Optimize queries**:
   - Use select with specific fields
   - Add indexes on frequently queried columns

3. **Monitor usage**:
   - Check Supabase dashboard → Usage

## Development Workflow

### Making Changes

1. **Backend code changes**:
   - Edit files in `backend/app/`
   - Auto-reloads with `--reload` flag
   - Test with curl or OpenAPI docs

2. **Frontend code changes**:
   - Edit files in `frontend/src/`
   - Auto-reloads with dev server
   - Test in browser at localhost:3000

3. **Database schema changes**:
   - Update `database/schema.sql`
   - Drop and recreate tables in Supabase
   - Re-run seeding scripts

### Running Both Services

**Option 1**: Two terminals
```bash
# Terminal 1
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2
cd frontend && npm run dev
```

**Option 2**: Using tmux/screen

**Option 3**: Docker Compose (not included, but recommended for production)

## Next Steps

After successful setup:

1. **Test with sample queries** (`data/sample_queries.json`)
2. **Explore API docs** (http://localhost:8000/docs)
3. **Review analytics** (http://localhost:8000/api/v1/analytics/stats)
4. **Check escalation queue** (http://localhost:8000/api/v1/escalations)
5. **Customize knowledge base** (add more documents to `knowledge-base/`)

## Getting Help

- **API Documentation**: http://localhost:8000/docs
- **Frontend README**: `frontend/README.md`
- **Supabase Guide**: `docs/SUPABASE_SETUP.md`
- **Architecture Overview**: `docs/ARCHITECTURE.md`

## Production Deployment

See separate deployment guide (not included in this MVP) for:
- Docker containerization
- Cloud deployment (AWS, GCP, Azure)
- Environment-specific configurations
- Monitoring and logging
- Backup strategies
