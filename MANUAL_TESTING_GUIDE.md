# BookLeaf AI Assistant - Manual Testing Guide

This guide provides step-by-step instructions to manually test the BookLeaf AI Assistant project with Supabase.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Testing](#database-testing)
4. [Backend API Testing](#backend-api-testing)
5. [Identity Resolution Testing](#identity-resolution-testing)
6. [Chat Functionality Testing](#chat-functionality-testing)
7. [Analytics Testing](#analytics-testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. VPN Setup (Required for India)

Your Supabase instance requires VPN access. Cloudflare WARP is already installed and connected.

**Verify VPN Connection:**
```bash
# Check WARP status
warp-cli status

# Should show: "Status update: Connected"
```

**If VPN is not connected:**
```bash
warp-cli connect
```

### 2. Environment Variables

Ensure your `.env` files are configured:

**Check Backend Configuration:**
```bash
cat backend/.env | grep -E "SUPABASE_URL|OPENAI_API_KEY"
```

**Expected Output:**
```
SUPABASE_URL=https://frpjbfuslgsirgdjdczy.supabase.co
OPENAI_API_KEY=sk-proj-...
```

---

## Environment Setup

### 1. Activate Virtual Environment

```bash
cd /Users/vaibhavee/project/BookLeaf_Assignment/backend
source venv/bin/activate
```

Your prompt should change to show `(venv)`.

### 2. Verify Dependencies

```bash
python -c "import supabase; import openai; import fastapi; print('✅ All core dependencies installed')"
```

---

## Database Testing

### Test 1: Connection Test

Run the comprehensive connection test:

```bash
cd /Users/vaibhavee/project/BookLeaf_Assignment
python3 test_supabase_connection.py
```

**Expected Output:**
```
============================================================
Supabase Connection Test
============================================================

Testing URL: https://frpjbfuslgsirgdjdczy.supabase.co
Key configured: Yes

Test 1: DNS Resolution
------------------------------------------------------------
✅ DNS resolved: frpjbfuslgsirgdjdczy.supabase.co -> 104.18.38.10

Test 2: HTTP Connection
------------------------------------------------------------
✅ HTTP connection successful: 401

Test 3: Supabase Client Connection
------------------------------------------------------------
✅ Supabase client connected successfully!
   Query successful: 20 rows returned

============================================================
Test Complete
============================================================
```

### Test 2: Verify Seeded Data

**Check Authors Count:**
```bash
cd backend
source venv/bin/activate
python3 << 'EOF'
from app.db.client import supabase

# Count authors
result = supabase.table("authors").select("*", count="exact").execute()
print(f"✅ Total Authors: {result.count}")

# Show first 3 authors
authors = supabase.table("authors").select("full_name, email").limit(3).execute()
print("\nSample Authors:")
for author in authors.data:
    print(f"  - {author['full_name']} ({author['email']})")
EOF
```

**Expected Output:**
```
✅ Total Authors: 20

Sample Authors:
  - Sarah Johnson (sarah.johnson@example.com)
  - Michael Chen (michael.chen@example.com)
  - Jennifer Smith (jennifer.smith@example.com)
```

**Check Identities Count:**
```bash
python3 << 'EOF'
from app.db.client import supabase

# Count identities
result = supabase.table("identities").select("*", count="exact").execute()
print(f"✅ Total Identities: {result.count}")

# Show identity platforms
identities = supabase.table("identities").select("platform").execute()
platforms = {}
for identity in identities.data:
    platform = identity['platform']
    platforms[platform] = platforms.get(platform, 0) + 1

print("\nIdentities by Platform:")
for platform, count in sorted(platforms.items()):
    print(f"  - {platform}: {count}")
EOF
```

**Expected Output:**
```
✅ Total Identities: 43

Identities by Platform:
  - email: 20
  - instagram: 4
  - phone: 15
  - whatsapp: 4
```

### Test 3: Query Specific Author

```bash
python3 << 'EOF'
from app.db.client import supabase

# Find Sarah Johnson
result = supabase.table("authors")\
    .select("*, identities(*)")\
    .eq("email", "sarah.johnson@example.com")\
    .execute()

if result.data:
    author = result.data[0]
    print(f"✅ Found Author: {author['full_name']}")
    print(f"   Email: {author['email']}")
    print(f"   Phone: {author['phone']}")
    print(f"   Identities: {len(author['identities'])}")
else:
    print("❌ Author not found")
EOF
```

---

## Backend API Testing

### 1. Start the Backend Server

```bash
cd /Users/vaibhavee/project/BookLeaf_Assignment/backend
source venv/bin/activate

# Kill any existing server on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Leave this terminal running and open a new terminal for testing.**

### 2. Test Health Endpoint

Open a **new terminal**:

```bash
curl http://localhost:8000/health | python3 -m json.tool
```

**Expected Output:**
```json
{
    "status": "healthy",
    "environment": "development",
    "version": "1.0.0"
}
```

### 3. Access API Documentation

Open your browser and visit:

```
http://localhost:8000/docs
```

You should see the **Swagger UI** with all available endpoints.

### 4. List Available Endpoints

```bash
curl -s http://localhost:8000/openapi.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Available API Endpoints:')
print('=' * 60)
for path, methods in sorted(data['paths'].items()):
    for method in methods.keys():
        print(f'{method.upper():7} {path}')
"
```

**Expected Output:**
```
Available API Endpoints:
============================================================
GET     /
GET     /health
POST    /api/v1/chat/message
GET     /api/v1/chat/conversation/{conversation_id}
POST    /api/v1/chat/conversation
POST    /api/v1/identity/resolve
GET     /api/v1/identity/author/{author_id}
GET     /api/v1/escalations/
GET     /api/v1/escalations/{escalation_id}
PATCH   /api/v1/escalations/{escalation_id}
POST    /api/v1/escalations/{escalation_id}/resolve
GET     /api/v1/analytics/stats
GET     /api/v1/analytics/confidence-distribution
```

---

## Identity Resolution Testing

### Test 1: Resolve Existing Author (Email)

```bash
curl -s -X POST http://localhost:8000/api/v1/identity/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sarah.johnson@example.com"
  }' | python3 -m json.tool
```

**Expected Output:**
```json
{
    "success": true,
    "author": {
        "id": "6204f070-f8d6-423f-bde1-196407aa9d1d",
        "full_name": "Sarah Johnson",
        "email": "sarah.johnson@example.com",
        "phone": "+1-555-0101",
        "metadata": {},
        "created_at": "2026-02-28T10:51:37.123456Z"
    },
    "identity": {
        "id": "7c9c07e6-3496-4864-9026-adc9f6b71351",
        "author_id": "6204f070-f8d6-423f-bde1-196407aa9d1d",
        "platform": "email",
        "platform_identifier": "sarah.johnson@example.com",
        "confidence_score": 1.0,
        "matching_method": "exact_match",
        "verified": true,
        "created_at": "2026-02-28T10:51:38.123456Z"
    },
    "confidence": 1.0,
    "method": "exact_match",
    "reasoning": "Exact email match found"
}
```

### Test 2: Resolve Existing Author (Phone)

```bash
curl -s -X POST http://localhost:8000/api/v1/identity/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1-555-0102"
  }' | python3 -m json.tool
```

**Expected:** Should match Michael Chen with high confidence.

### Test 3: Resolve with Name Matching

```bash
curl -s -X POST http://localhost:8000/api/v1/identity/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sarah Johnson",
    "email": "sarah.j.new@example.com"
  }' | python3 -m json.tool
```

**Expected:** Should use fuzzy matching to find Sarah Johnson even with a different email.

### Test 4: Create New Author

```bash
curl -s -X POST http://localhost:8000/api/v1/identity/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Test User",
    "email": "john.test@example.com",
    "phone": "+1-555-9999"
  }' | python3 -m json.tool
```

**Expected Output:**
```json
{
    "success": true,
    "author": {
        "id": "NEW-UUID",
        "full_name": "John Test User",
        "email": "john.test@example.com",
        "phone": "+1-555-9999",
        "metadata": {
            "created_from": "web_chat",
            "initial_identifier": "john.test@example.com"
        },
        "created_at": "2026-02-28T..."
    },
    "confidence": 0.5,
    "method": "new_identity_created",
    "reasoning": "No existing match found, created new author profile"
}
```

### Test 5: Get Author by ID

First, get an author ID from the resolve test, then:

```bash
curl -s http://localhost:8000/api/v1/identity/author/6204f070-f8d6-423f-bde1-196407aa9d1d \
  | python3 -m json.tool
```

---

## Chat Functionality Testing

### Test 1: Simple Chat Message

```bash
curl -s -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I need help with my manuscript",
    "identifier": {
      "email": "sarah.johnson@example.com"
    }
  }' | python3 -m json.tool
```

**Note:** If this returns an error, it's likely due to the chat processor bug we identified. The identity resolution itself is working correctly.

### Test 2: Chat with Name Introduction

```bash
curl -s -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi, my name is Michael Chen. Can you check the status of my book?",
    "identifier": {
      "email": "michael.chen@example.com"
    }
  }' | python3 -m json.tool
```

### Test 3: Create Conversation

```bash
curl -s -X POST http://localhost:8000/api/v1/chat/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "author_id": "6204f070-f8d6-423f-bde1-196407aa9d1d",
    "channel": "web_chat"
  }' | python3 -m json.tool
```

---

## Analytics Testing

### Test 1: Get Statistics

```bash
curl -s http://localhost:8000/api/v1/analytics/stats | python3 -m json.tool
```

**Expected Output:**
```json
{
    "total_conversations": 0,
    "total_messages": 0,
    "total_escalations": 0,
    "avg_confidence_score": 0.0,
    "resolved_escalations": 0,
    "pending_escalations": 0
}
```

### Test 2: Confidence Distribution

```bash
curl -s http://localhost:8000/api/v1/analytics/confidence-distribution \
  | python3 -m json.tool
```

---

## Testing via Swagger UI

### Option: Interactive Testing

1. Open browser: http://localhost:8000/docs
2. Click on any endpoint (e.g., **POST /api/v1/identity/resolve**)
3. Click **"Try it out"**
4. Enter test data:
   ```json
   {
     "email": "sarah.johnson@example.com"
   }
   ```
5. Click **"Execute"**
6. View the response below

**Advantages:**
- Interactive interface
- Automatic request formatting
- Easy to test different parameters
- View all available endpoints

---

## Test Scenarios

### Scenario 1: New User Registration Flow

**Step 1:** User submits contact form
```bash
curl -s -X POST http://localhost:8000/api/v1/identity/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Williams",
    "email": "alice.w@example.com",
    "phone": "+1-555-7777"
  }' | python3 -m json.tool
```

**Verify:**
- New author created ✅
- New identity created ✅
- Confidence score = 0.5 ✅

**Step 2:** User sends message with same email
```bash
curl -s -X POST http://localhost:8000/api/v1/identity/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice.w@example.com"
  }' | python3 -m json.tool
```

**Verify:**
- Same author returned ✅
- Exact match found ✅
- Confidence score = 1.0 ✅

### Scenario 2: Multi-Channel Identity Linking

**Step 1:** User contacts via email
```bash
curl -s -X POST http://localhost:8000/api/v1/identity/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob.smith@example.com",
    "name": "Bob Smith"
  }' | python3 -m json.tool
```

**Step 2:** Same user contacts via phone
```bash
curl -s -X POST http://localhost:8000/api/v1/identity/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1-555-8888",
    "name": "Bob Smith"
  }' | python3 -m json.tool
```

**Verify:**
- Fuzzy name matching works ✅
- Both identities linked to same author ✅

### Scenario 3: Verify Database Persistence

**Step 1:** Create a test author via API
```bash
curl -s -X POST http://localhost:8000/api/v1/identity/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Persistence",
    "email": "test.persist@example.com"
  }' | python3 -m json.tool | grep '"id"' | head -1
```

Copy the author ID from the response.

**Step 2:** Query directly from Supabase
```bash
cd backend
source venv/bin/activate
python3 << 'EOF'
from app.db.client import supabase

result = supabase.table("authors")\
    .select("*")\
    .eq("email", "test.persist@example.com")\
    .execute()

if result.data:
    print("✅ Author found in database!")
    print(f"   Name: {result.data[0]['full_name']}")
    print(f"   Email: {result.data[0]['email']}")
else:
    print("❌ Author not found in database")
EOF
```

**Step 3:** Stop server, restart, and query again
```bash
# In server terminal: Press Ctrl+C
# Then restart:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# In test terminal:
curl -s -X POST http://localhost:8000/api/v1/identity/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.persist@example.com"
  }' | python3 -m json.tool
```

**Verify:**
- Data persists after server restart ✅
- Same author ID returned ✅

---

## Troubleshooting

### Issue 1: Connection Refused

**Symptom:**
```
curl: (7) Failed to connect to localhost port 8000
```

**Solution:**
```bash
# Check if server is running
lsof -i:8000

# If not running, start it:
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Issue 2: DNS Resolution Failed

**Symptom:**
```
❌ DNS resolution failed: Could not resolve host
```

**Solution:**
```bash
# Check VPN status
warp-cli status

# If not connected:
warp-cli connect

# Wait 5 seconds and test again
sleep 5
python3 test_supabase_connection.py
```

### Issue 3: Module Not Found

**Symptom:**
```
ModuleNotFoundError: No module named 'supabase'
```

**Solution:**
```bash
cd backend
source venv/bin/activate

# Verify activation
which python
# Should show: /Users/vaibhavee/project/BookLeaf_Assignment/backend/venv/bin/python

# Install dependencies
pip install supabase python-dotenv
```

### Issue 4: OpenAI API Error

**Symptom:**
```
error: Invalid API Key
```

**Solution:**
```bash
# Check if key is set
cat backend/.env | grep OPENAI_API_KEY

# If empty or invalid, update it:
nano backend/.env
# Add: OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY
```

### Issue 5: Port Already in Use

**Symptom:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Wait and restart
sleep 2
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Quick Test Checklist

Use this checklist for rapid testing:

- [ ] VPN connected (`warp-cli status`)
- [ ] Environment variables set (`cat backend/.env`)
- [ ] Virtual environment activated (`which python`)
- [ ] Database connection works (`python3 test_supabase_connection.py`)
- [ ] Backend server running (`curl http://localhost:8000/health`)
- [ ] Can resolve existing identity (`curl -X POST ... /identity/resolve`)
- [ ] Can create new author (`curl -X POST ... /identity/resolve` with new email)
- [ ] API docs accessible (`open http://localhost:8000/docs`)
- [ ] Data persists in database (query via Supabase)

---

## Performance Testing

### Load Test (Optional)

```bash
# Install apache bench if not available
# brew install httpd

# Test health endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:8000/health

# Test identity resolution (50 requests, 5 concurrent)
ab -n 50 -c 5 -p payload.json -T application/json \
  http://localhost:8000/api/v1/identity/resolve
```

Create `payload.json`:
```json
{
  "email": "sarah.johnson@example.com"
}
```

---

## Success Criteria

Your system is working correctly if:

1. ✅ VPN connects successfully
2. ✅ DNS resolves Supabase URL
3. ✅ Database has 20 authors and 43 identities
4. ✅ Backend server starts without errors
5. ✅ Health endpoint returns 200 OK
6. ✅ Identity resolution works for existing users
7. ✅ New authors can be created
8. ✅ Data persists across server restarts
9. ✅ API documentation is accessible
10. ✅ All endpoints return expected status codes

---

## Next Steps

After completing manual testing:

1. **Run Automated Tests:**
   ```bash
   cd backend
   pytest tests/ -v
   ```

2. **Check Coverage:**
   ```bash
   pytest --cov=app tests/
   ```

3. **Review Logs:**
   ```bash
   # Check for warnings or errors
   grep -i "error\|warning" logs/app.log
   ```

4. **Supabase Dashboard:**
   - Visit: https://supabase.com/dashboard
   - Check Tables: authors, identities, conversations
   - Review API logs

---

## Support

If you encounter issues not covered in this guide:

1. Check server logs in the terminal
2. Review Supabase dashboard for database errors
3. Verify all environment variables are set correctly
4. Ensure VPN is connected and stable
5. Try restarting the backend server

---

**Last Updated:** 2026-02-28
**Version:** 1.0.0
