# Create New Supabase Project (Fresh Start)

Since your current project has DNS issues, let's create a new one.

## Step 1: Create Project (2 minutes)

1. Go to: https://supabase.com/dashboard
2. Click: **"New Project"**
3. Fill in:
   - **Name**: `bookleaf-ai-new`
   - **Database Password**: (save this securely!)
   - **Region**: Choose **US East (Ohio)** or **Europe (Frankfurt)**
     - ⚠️ **DO NOT choose Southeast Asia** (has infrastructure issues)
4. Click: **"Create new project"**
5. Wait 2-3 minutes for provisioning

## Step 2: Enable Vector Extension (30 seconds)

1. Go to: **Database → Extensions**
2. Search for: **"vector"**
3. Click: **Enable** on "vector" extension
4. Wait for confirmation

## Step 3: Run Database Schema (1 minute)

1. Go to: **SQL Editor**
2. Click: **"New Query"**
3. Copy the entire contents of:
   ```
   /Users/vaibhavee/project/Bookleaf_Assignment/database/schema.sql
   ```
4. Paste into SQL Editor
5. Click: **"Run"**
6. Verify: You should see 8 tables created

## Step 4: Get API Credentials (30 seconds)

1. Go to: **Project Settings → API**
2. Copy these values:

   - **Project URL**: `https://xxxxxxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **service_role secret key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## Step 5: Update Environment Variables

Update `/Users/vaibhavee/project/Bookleaf_Assignment/backend/.env`:

```bash
# Replace with your NEW project credentials
SUPABASE_URL=https://YOUR-NEW-PROJECT.supabase.co
SUPABASE_KEY=your-new-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-new-service-role-key

# Keep your OpenAI key
OPENAI_API_KEY=sk-proj-YOUR-OPENAI-API-KEY-HERE
```

## Step 6: Test New Connection (30 seconds)

```bash
cd /Users/vaibhavee/project/Bookleaf_Assignment

# Test DNS (should work now!)
nslookup YOUR-NEW-PROJECT.supabase.co

# Test connection
cd backend && source venv/bin/activate
python3 -c "
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
result = client.table('authors').select('id').limit(1).execute()
print('✅ SUCCESS! Connected to new Supabase project')
"
```

## Step 7: Seed Database (1 minute)

```bash
cd /Users/vaibhavee/project/Bookleaf_Assignment/backend
source venv/bin/activate

# Seed 20 mock authors
python3 scripts/seed_data.py
# Type: y (when asked to clear data)
```

**Expected output:**
```
✅ Seeding completed successfully!
Authors created: 20
Identities created: 41
```

## Step 8: Generate Embeddings (2 minutes) - OPTIONAL

**Only if you have OpenAI API key:**

```bash
python3 scripts/prepare_knowledge_base.py
# Type: y (when asked to clear data)
```

**Expected output:**
```
✅ Knowledge Base Preparation Completed!
Documents processed: 4
Total embeddings: 50-100
```

**If no OpenAI key**: Skip this step. System will use local keyword search (works fine!).

## Step 9: Restart Backend

```bash
# Stop current server
pkill -f uvicorn

# Start with new Supabase connection
cd /Users/vaibhavee/project/Bookleaf_Assignment/backend
source venv/bin/activate
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Look for in logs:**
```
✅ supabase_client_initialized
```

## Step 10: Test API

```bash
# Health check
curl http://localhost:8001/health
```

**Should show:**
```json
{
  "status": "healthy",
  "database": "supabase",
  "authors_count": 20
}
```

## Step 11: Test Query

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

## ✅ Done!

Your BookLeaf AI Assistant now runs on:
- ✅ Fresh Supabase project (working DNS)
- ✅ 20 mock authors with data
- ✅ Knowledge base loaded
- ✅ Vector search (if OpenAI embeddings generated)
- ✅ Full production features

## No VPN Needed!

With US East or Europe region, you **don't need VPN** - it works directly from India!

---

## Troubleshooting

### Still can't connect?

```bash
# Check which region you chose
# If Southeast Asia → recreate with US East or Europe
```

### OpenAI embedding fails?

```bash
# It's optional! System works fine without it
# Local keyword search is used as fallback
```

### Tables not created?

```bash
# Re-run schema.sql in SQL Editor
# Check for error messages
```

---

**Total time: ~5-7 minutes** to get a working Supabase setup!
