# Supabase Setup Guide

This guide walks you through setting up Supabase for the BookLeaf AI Assistant project.

## Prerequisites

- A Supabase account (sign up at [https://supabase.com](https://supabase.com))
- Basic understanding of PostgreSQL
- Your OpenAI API key ready

## Step 1: Create a New Supabase Project

1. Log in to your Supabase dashboard at [https://app.supabase.com](https://app.supabase.com)

2. Click **"New Project"**

3. Fill in the project details:
   - **Name**: `bookleaf-ai-assistant` (or your preferred name)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose the closest region to your location
   - **Pricing Plan**: Free tier is sufficient for development

4. Click **"Create new project"** and wait 2-3 minutes for provisioning

## Step 2: Enable pgvector Extension

The pgvector extension is required for vector similarity search (RAG system).

1. In your Supabase project dashboard, go to **Database** → **Extensions** (left sidebar)

2. Search for **"vector"** or scroll to find **"pgvector"**

3. Click the toggle to **Enable** the pgvector extension

4. Verify it's enabled (the toggle should be green/on)

**Alternative: Enable via SQL Editor**

1. Go to **SQL Editor** in the left sidebar
2. Click **"New query"**
3. Run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. Click **"Run"** or press `Ctrl+Enter`

## Step 3: Run the Database Schema

1. Go to **SQL Editor** in the left sidebar

2. Click **"New query"**

3. Copy the entire contents of `database/schema.sql` from this project

4. Paste it into the SQL editor

5. Click **"Run"** or press `Ctrl+Enter`

6. You should see success messages for each table created

### Verify Schema Creation

Run this query to verify all tables were created:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

You should see these tables:
- authors
- conversations
- escalations
- identities
- knowledge_documents
- knowledge_embeddings
- messages
- query_analytics

## Step 4: Get Your API Credentials

You'll need three pieces of information:

### 4.1 Project URL

1. Go to **Settings** → **API** (left sidebar)
2. Find **"Project URL"** under "Config"
3. Copy the URL (format: `https://xxxxxxxxxxxxx.supabase.co`)

### 4.2 Anon/Public Key

1. On the same **Settings** → **API** page
2. Find **"Project API keys"** section
3. Copy the **"anon"** **"public"** key (this is safe for frontend use)

### 4.3 Service Role Key

1. On the same page, find **"service_role"** key
2. Click **"Reveal"** then **"Copy"**
3. ⚠️ **IMPORTANT**: Keep this secret! Never commit to git or expose to frontend

## Step 5: Configure Environment Variables

1. Navigate to your backend directory:
   ```bash
   cd backend
   ```

2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your credentials:
   ```bash
   # Supabase Configuration
   SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # anon key
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # service_role key

   # OpenAI Configuration
   OPENAI_API_KEY=sk-...  # Your OpenAI API key
   ```

4. Save the file

## Step 6: Test the Connection

1. Create a test script `backend/test_supabase.py`:
   ```python
   from supabase import create_client
   from dotenv import load_dotenv
   import os

   load_dotenv()

   supabase = create_client(
       os.getenv("SUPABASE_URL"),
       os.getenv("SUPABASE_KEY")
   )

   # Test query
   result = supabase.table("authors").select("*").limit(5).execute()
   print(f"Connection successful! Found {len(result.data)} authors")
   ```

2. Run the test:
   ```bash
   python test_supabase.py
   ```

3. You should see: `Connection successful! Found 0 authors` (or more if you've seeded data)

## Step 7: Seed Mock Data

1. Ensure you're in the backend directory with venv activated:
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Run the seeding script:
   ```bash
   python scripts/seed_data.py
   ```

3. You should see output confirming 20 authors were created

4. Verify in Supabase:
   - Go to **Table Editor** → **authors**
   - You should see 20 author records

## Step 8: Generate Knowledge Base Embeddings

1. Ensure knowledge base documents exist in `knowledge-base/` directory

2. Run the embedding generation script:
   ```bash
   python scripts/prepare_knowledge_base.py
   ```

3. This will:
   - Chunk each document into 500-token pieces
   - Generate embeddings using OpenAI
   - Store in `knowledge_embeddings` table

4. Verify in Supabase:
   - Go to **Table Editor** → **knowledge_embeddings**
   - You should see 50-100 embedding records

## Troubleshooting

### Error: "relation 'authors' does not exist"

**Solution**: The schema wasn't created properly. Go back to Step 3 and run the schema SQL again.

### Error: "permission denied for extension pgvector"

**Solution**: Make sure you enabled the pgvector extension in Step 2.

### Error: "Invalid API key"

**Solution**:
- Verify you copied the entire key (they're very long)
- Make sure you're using the correct key type (anon vs service_role)
- Check for extra spaces or line breaks

### Error: "SSL connection required"

**Solution**: Supabase requires SSL. The Python client handles this automatically, but if you see this error, add `?sslmode=require` to your connection string.

### Slow Vector Queries

**Solution**: The ivfflat index needs tuning. Try:
```sql
-- Adjust lists parameter based on your data size
-- General rule: lists = rows / 1000
DROP INDEX IF EXISTS idx_knowledge_embeddings_vector;
CREATE INDEX idx_knowledge_embeddings_vector ON knowledge_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);  -- Adjust based on your data size
```

## Optional: Set Up Row Level Security (RLS)

For production, you should enable RLS policies. Here's a basic example:

```sql
-- Enable RLS on all tables
ALTER TABLE authors ENABLE ROW LEVEL SECURITY;
ALTER TABLE identities ENABLE ROW LEVEL SECURITY;
-- ... repeat for all tables

-- Example policy: Allow all operations for service role
CREATE POLICY "Service role has full access" ON authors
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);
```

For development, you can skip RLS and use the service role key.

## Monitoring and Maintenance

### Monitor Database Size

Go to **Settings** → **Usage** to monitor:
- Database size (Free tier: 500 MB)
- API requests
- Bandwidth

### View Logs

Go to **Logs** in the left sidebar to see:
- Database queries
- API requests
- Errors and warnings

### Backup

Supabase Free tier includes daily backups. For manual backups:
1. Go to **Database** → **Backups**
2. Click **"Start a backup"**

## Next Steps

After completing this setup:

1. ✅ Verify all tables exist in Table Editor
2. ✅ Confirm pgvector extension is enabled
3. ✅ Test connection with `test_supabase.py`
4. ✅ Seed 20 mock authors
5. ✅ Generate knowledge base embeddings
6. ✅ Start the FastAPI backend: `uvicorn app.main:app --reload`

You're now ready to use the BookLeaf AI Assistant!

## Support

- **Supabase Docs**: [https://supabase.com/docs](https://supabase.com/docs)
- **pgvector**: [https://github.com/pgvector/pgvector](https://github.com/pgvector/pgvector)
- **Project Issues**: See `README.md` for contact info
