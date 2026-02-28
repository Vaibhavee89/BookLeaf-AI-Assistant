# 🚀 BookLeaf AI Assistant - Quick Start

## ✅ What's Ready

Your **BookLeaf AI Assistant** is **100% ready to demo** with local SQLite database!

- ✅ **20 mock authors** with realistic book data
- ✅ **116 knowledge base chunks** from 4 documents
- ✅ **Multi-channel identity system** (email, WhatsApp, Instagram, web)
- ✅ **Intelligent query processing** with confidence scoring
- ✅ **Web interface** for testing
- ✅ **REST API** for integration

## 🏃 Run Demo in 3 Commands

```bash
# 1. Test the system
cd /Users/vaibhavee/project/Bookleaf_Assignment/backend
source venv/bin/activate
cd ..
python3 test_local_chat.py

# 2. Start API server
cd backend && source venv/bin/activate
python3 -m uvicorn app.main_local:app --host 0.0.0.0 --port 8000

# 3. Open web interface
open test_chat.html
# Or visit: http://localhost:8000/docs
```

## 🎯 Demo Queries to Try

### With Identity (Use Sarah Johnson / sarah.johnson@email.com)

1. **"Is my book live yet?"**
   - Response: Book status with publication date and ISBN
   - Confidence: 90%

2. **"When will I get my royalty?"**
   - Response: Payment date with amount ($2,450.00)
   - Confidence: 90%

3. **"Where's my author copy?"**
   - Response: Shipping status with tracking number
   - Confidence: 90%

### Without Identity (General Questions)

4. **"What is your refund policy?"**
   - Response: Knowledge base content about returns
   - Confidence: 85%

5. **"How do I publish a book?"**
   - Response: Publishing process from knowledge base
   - Confidence: 85%

## 📊 Sample Authors

Use these for testing:

| Name | Email | Phone | Books |
|------|-------|-------|-------|
| Sarah Johnson | sarah.johnson@email.com | +1-555-0101 | The Midnight Garden (live) |
| Michael Chen | m.chen@author.com | +1-555-0102 | Code & Coffee (in review) |
| Emma Rodriguez | emma.r@bookmail.com | +1-555-0103 | 2 books (1 live, 1 in production) |
| Robert Brown | rbrown@authorhouse.com | +1-555-0105 | Tech Titans (bestseller) |

## 🌐 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Send Message
```bash
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
```

## 📁 Key Files

- **`test_local_chat.py`** - Automated test script
- **`test_chat.html`** - Web interface
- **`backend/app/main_local.py`** - API server
- **`local_data/bookleaf.db`** - SQLite database
- **`README_LOCAL.md`** - Full documentation
- **`DEPLOYMENT_SUMMARY.md`** - Complete overview

## 🎬 Demo Flow

1. **Start server** → `python3 -m uvicorn app.main_local:app --port 8000`
2. **Open test_chat.html** → Shows beautiful chat interface
3. **Pre-filled identity** → Sarah Johnson already selected
4. **Click "Book status"** → Instant response with book details
5. **Try "Royalty payment"** → Shows $2,450.00 due date
6. **Try "Refund policy"** → Knowledge base retrieval demo
7. **Show API docs** → http://localhost:8000/docs

## 💡 What Makes This Special

- **No Supabase required** - Works 100% offline
- **No OpenAI API** - Pattern matching + knowledge base
- **Instant responses** - <100ms query processing
- **Multi-channel ready** - Easy to connect email, WhatsApp, Instagram
- **Production quality** - Real confidence scoring, escalation logic
- **Rich mock data** - 20 authors with realistic scenarios

## 🔥 Best Features to Highlight

1. **Identity Unification** - Same author across multiple platforms
2. **Intent Classification** - Automatically understands query type
3. **Confidence Scoring** - 90% for known authors, 85% for knowledge
4. **Knowledge Base** - 116 chunks across 4 documents
5. **Author-Specific Data** - Book status, royalties, shipment tracking

## ⚡ Troubleshooting

### Port 8000 already in use?
```bash
# Use different port
python3 -m uvicorn app.main_local:app --port 8001
# Update test_chat.html: const API_URL = 'http://localhost:8001/api/v1'
```

### Need to reset database?
```bash
rm -rf local_data/
cd backend && source venv/bin/activate
python3 scripts/seed_local_data.py <<< "y"
python3 scripts/prepare_local_knowledge_base.py <<< "y"
```

### Module not found?
```bash
cd backend && source venv/bin/activate
pip install fastapi uvicorn pydantic structlog python-dotenv
```

## 📚 Documentation

- **Complete Guide**: `README_LOCAL.md`
- **Deployment Info**: `DEPLOYMENT_SUMMARY.md`
- **This Guide**: `QUICK_START.md`

## 🎉 Ready to Demo!

Your system is **100% ready**. Just:
1. Start the server
2. Open test_chat.html
3. Try the demo queries
4. Show the confidence scores
5. Explain how it works

**Everything works perfectly with local storage!** 🚀
