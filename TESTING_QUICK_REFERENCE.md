# BookLeaf - Testing Quick Reference Card

Quick commands for testing the BookLeaf AI Assistant.

---

## 🚀 Quick Start

```bash
# 1. Ensure VPN is connected
warp-cli status

# 2. Navigate to project
cd /Users/vaibhavee/project/BookLeaf_Assignment/backend

# 3. Activate environment
source venv/bin/activate

# 4. Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🔍 Quick Tests

### Health Check
```bash
curl http://localhost:8000/health
```

### Test Database Connection
```bash
python3 test_supabase_connection.py
```

### Resolve Identity (Existing)
```bash
curl -X POST http://localhost:8000/api/v1/identity/resolve \
  -H "Content-Type: application/json" \
  -d '{"email": "sarah.johnson@example.com"}' | python3 -m json.tool
```

### Create New Author
```bash
curl -X POST http://localhost:8000/api/v1/identity/resolve \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}' | python3 -m json.tool
```

---

## 📊 Database Queries

### Count Authors
```bash
python3 << 'EOF'
from app.db.client import supabase
result = supabase.table("authors").select("*", count="exact").execute()
print(f"Total Authors: {result.count}")
EOF
```

### List Authors
```bash
python3 << 'EOF'
from app.db.client import supabase
authors = supabase.table("authors").select("full_name, email").limit(10).execute()
for a in authors.data:
    print(f"{a['full_name']:20} {a['email']}")
EOF
```

### Find by Email
```bash
python3 << 'EOF'
from app.db.client import supabase
result = supabase.table("authors").select("*").eq("email", "sarah.johnson@example.com").execute()
print(result.data[0] if result.data else "Not found")
EOF
```

---

## 🔧 Troubleshooting

### Kill Process on Port 8000
```bash
lsof -ti:8000 | xargs kill -9
```

### Check VPN
```bash
warp-cli status
warp-cli connect  # if not connected
```

### Verify Environment
```bash
cat backend/.env | grep -E "SUPABASE_URL|OPENAI_API_KEY"
```

### Re-seed Database
```bash
cd backend
source venv/bin/activate
echo "y" | python scripts/seed_data.py
```

---

## 📚 Useful URLs

- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health
- **Supabase Dashboard:** https://supabase.com/dashboard
- **Full Guide:** See `MANUAL_TESTING_GUIDE.md`

---

## 🎯 Sample Test Data

### Existing Authors (from seed)
- Sarah Johnson: `sarah.johnson@example.com` / `+1-555-0101`
- Michael Chen: `michael.chen@example.com` / `+1-555-0102`
- Jennifer Smith: `jennifer.smith@example.com` / `+1-555-0103`

### Test Payloads

**Identity Resolution:**
```json
{
  "name": "Sarah Johnson",
  "email": "sarah.johnson@example.com"
}
```

**Create New:**
```json
{
  "name": "New User",
  "email": "newuser@example.com",
  "phone": "+1-555-9999"
}
```

---

## ⚡ One-Liner Tests

```bash
# Full test suite
warp-cli status && python3 test_supabase_connection.py && curl http://localhost:8000/health

# Check if everything is running
ps aux | grep -E "uvicorn|warp-cli" | grep -v grep

# Get all endpoints
curl -s http://localhost:8000/openapi.json | python3 -c "import sys,json;d=json.load(sys.stdin);[print(f'{m.upper():7} {p}') for p,ms in d['paths'].items() for m in ms]"
```

---

**For full testing guide, see:** `MANUAL_TESTING_GUIDE.md`
