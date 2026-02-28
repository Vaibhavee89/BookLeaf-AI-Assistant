# Switch from Local SQLite to Supabase

## Prerequisites

✅ Supabase dashboard shows "Healthy"
⚠️ **You must be connected to VPN** (if your country blocks Supabase)

## Step 1: Verify VPN Connection

**Connect to your VPN first**, then test:

```bash
# Test DNS resolution
nslookup frpjbfuslgsirqdjdczy.supabase.co

# Should show an IP address, not "NXDOMAIN"
```

If still failing, try:
```bash
# Clear DNS cache
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# Test again
nslookup frpjbfuslgsirqdjdczy.supabase.co
```

## Step 2: Test Supabase Connection

```bash
cd /Users/vaibhavee/project/Bookleaf_Assignment
bash test_your_supabase.sh
```

**Expected output:**
```
✅ SUCCESS! Supabase is accessible
   Authors table query worked
```

## Step 3: Verify Database Schema

Check that all tables exist in Supabase:

```bash
# Go to your Supabase dashboard
# Navigate to: Table Editor
# You should see these tables:
- authors
- identities
- conversations
- messages
- knowledge_documents
- knowledge_embeddings
- escalations
- query_analytics
```

If tables are missing:
```bash
# Re-run the schema
# Go to SQL Editor in Supabase dashboard
# Copy contents of database/schema.sql
# Paste and execute
```

## Step 4: Seed Supabase Database

```bash
cd /Users/vaibhavee/project/Bookleaf_Assignment/backend
source venv/bin/activate

# Seed 20 mock authors
python3 scripts/seed_data.py

# When prompted "Do you want to clear existing data first? (y/N):"
# Type: y
```

**Expected output:**
```
✅ Seeding completed successfully!
============================================================
Authors created: 20
Identities created: 41
============================================================
```

## Step 5: Generate Knowledge Base Embeddings

**Note:** This requires OpenAI API key

```bash
cd /Users/vaibhavee/project/Bookleaf_Assignment/backend
source venv/bin/activate

# Check if OpenAI key is set
grep OPENAI_API_KEY .env

# If key is present, generate embeddings
python3 scripts/prepare_knowledge_base.py

# When prompted "Do you want to clear existing knowledge base data? (y/N):"
# Type: y
```

**Expected output:**
```
✅ Knowledge Base Preparation Completed!
============================================================
Documents processed: 4
Documents successful: 4
Total embeddings: 50-100
============================================================
```

**If you don't have OpenAI API key**, the system will use the local knowledge base (keyword search) which works fine for demo purposes.

## Step 6: Update Backend to Use Supabase

The backend automatically detects Supabase availability. Restart the server:

```bash
cd /Users/vaibhavee/project/Bookleaf_Assignment/backend
source venv/bin/activate

# Stop any running servers
pkill -f uvicorn

# Start with Supabase detection
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Check logs for:**
```
✅ supabase_client_initialized
```

If you see `using_local_database_fallback`, Supabase isn't accessible yet.

## Step 7: Test Supabase Connection

```bash
# Test API with Supabase
curl http://localhost:8001/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "supabase",  // Should say "supabase", not "sqlite"
  "authors_count": 20
}
```

## Step 8: Test Query with Supabase

```bash
curl -X POST http://localhost:8001/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Is my book live yet?",
    "identity": {
      "name": "Sarah Johnson",
      "email": "sarah.johnson@email.com",
      "platform": "web_chat"
    }
  }'
```

**Check response metadata:**
```json
{
  "metadata": {
    "processing_method": "supabase"  // Should say "supabase"
  }
}
```

## Troubleshooting

### DNS Still Fails Even on VPN

Try using Cloudflare Worker proxy:

```bash
# Update backend/.env
SUPABASE_URL=https://bookleaf-supabase-proxy.vaibhaveesingh89.workers.dev
```

### "Table does not exist" Error

Re-run schema:
```bash
# In Supabase dashboard: SQL Editor
# Run: database/schema.sql
```

### "No OpenAI API Key" Error

Either:
1. Add OpenAI key to `.env`: `OPENAI_API_KEY=sk-...`
2. Or keep using local mode (works fine without OpenAI)

### Seeding Fails

Check Supabase connection:
```bash
cd backend && source venv/bin/activate
python3 -c "
from app.db.client import supabase
result = supabase.table('authors').select('id').limit(1).execute()
print('✅ Connected!' if result.data is not None else '❌ Failed')
"
```

## Verification Checklist

- [ ] VPN connected (if needed)
- [ ] DNS resolves Supabase domain
- [ ] Python Supabase client connects
- [ ] Database tables exist
- [ ] 20 authors seeded
- [ ] Knowledge base loaded (optional: with embeddings)
- [ ] Backend server uses Supabase
- [ ] API responds with Supabase metadata
- [ ] Web interface works with Supabase

## Rollback to Local Mode

If Supabase issues continue:

```bash
# The system automatically falls back to local SQLite
# Just restart the server:
cd backend && source venv/bin/activate
python3 -m uvicorn app.main_local:app --host 0.0.0.0 --port 8001

# Or stop VPN and use local mode
```

## Benefits of Supabase Mode

✅ **Vector similarity search** - More accurate knowledge retrieval
✅ **LLM-powered responses** - Natural language generation
✅ **Real-time sync** - Multiple instances can share data
✅ **Scalability** - Production-ready cloud database
✅ **PostgreSQL features** - Full SQL capabilities

## Current Status

Your local SQLite mode is **100% functional** and ready to demo. Switching to Supabase is optional and provides enhanced features, but the core functionality works perfectly with local storage.

---

**Next Step:** Connect to VPN, then run `bash test_your_supabase.sh` to verify connectivity.
