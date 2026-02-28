# 🐳 Docker Deployment Guide

Deploy your BookLeaf AI Assistant using Docker (more reliable than Vercel serverless for complex apps).

---

## 🎯 Why Docker?

- ✅ **Consistent environment** - Works everywhere
- ✅ **All dependencies included** - No version conflicts
- ✅ **Easier debugging** - Better error messages
- ✅ **More control** - Full Python environment
- ✅ **Works with Supabase** - Direct connection via VPN

---

## 🚀 Deployment Options

### Option 1: Deploy to Render.com (Easiest - Free Tier Available)

**Best for:** Quick deployment with free hosting

#### Step 1: Create render.yaml

Already created! Your `render.yaml` is ready.

#### Step 2: Push to GitHub

```bash
# Already done - your code is on GitHub
git push origin main
```

#### Step 3: Deploy to Render

1. **Go to:** https://render.com/
2. **Sign up** with GitHub
3. **New → Blueprint**
4. **Connect repository:** Vaibhavee89/BookLeaf-AI-Assistant
5. **Add Environment Variables:**
   - `OPENAI_API_KEY` = (your new key)
   - `SUPABASE_URL` = https://frpjbfuslgsirgdjdczy.supabase.co
   - `SUPABASE_KEY` = (your anon key)
   - `SUPABASE_SERVICE_ROLE_KEY` = (your service key)
6. **Click "Apply"**

⏱️ Wait 5-10 minutes for deployment.

---

### Option 2: Deploy to Railway.app (Recommended)

**Best for:** Easy deployment with excellent developer experience

#### Step 1: Deploy to Railway

1. **Go to:** https://railway.app/
2. **Sign in** with GitHub
3. **New Project → Deploy from GitHub repo**
4. **Select:** Vaibhavee89/BookLeaf-AI-Assistant
5. **Railway will auto-detect** Docker configuration

#### Step 2: Add Environment Variables

In Railway dashboard:
- Click on your service
- Go to "Variables" tab
- Add:
  ```
  OPENAI_API_KEY=sk-proj-YOUR-NEW-KEY
  SUPABASE_URL=https://frpjbfuslgsirgdjdczy.supabase.co
  SUPABASE_KEY=your-anon-key
  SUPABASE_SERVICE_ROLE_KEY=your-service-key
  NEXT_PUBLIC_API_URL=${{RAILWAY_PUBLIC_DOMAIN}}
  ```

#### Step 3: Deploy

Railway auto-deploys! You'll get URLs like:
- Frontend: `https://your-app.railway.app`
- Backend: `https://your-api.railway.app`

---

### Option 3: Local Docker (For Testing)

#### Test Locally

```bash
# Navigate to project
cd /Users/vaibhavee/project/BookLeaf_Assignment

# Create .env file
cat > .env << 'EOF'
OPENAI_API_KEY=sk-proj-YOUR-NEW-KEY
SUPABASE_URL=https://frpjbfuslgsirgdjdczy.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key
EOF

# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up --build

# Or just backend
docker-compose -f docker-compose.prod.yml up backend

# Or just frontend
docker-compose -f docker-compose.prod.yml up frontend
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

### Option 4: Deploy to DigitalOcean App Platform

**Best for:** Production-ready deployment with auto-scaling

#### Step 1: Create App

1. **Go to:** https://cloud.digitalocean.com/apps
2. **Create App**
3. **Connect GitHub:** Vaibhavee89/BookLeaf-AI-Assistant
4. **Select:** Docker deployment type

#### Step 2: Configure

- **Dockerfile Path:** `backend/Dockerfile`
- **HTTP Port:** 8000
- **Environment Variables:** Add all Supabase & OpenAI keys

#### Step 3: Add Frontend

- **New Component** → Docker
- **Dockerfile Path:** `frontend/Dockerfile`
- **HTTP Port:** 3000

**Cost:** $5-12/month

---

### Option 5: AWS ECS / Google Cloud Run

For enterprise deployment - see detailed guides in docs.

---

## 🔧 Fix Vercel Deployment (Alternative)

If you still want to use Vercel:

### Clear Vercel Cache

1. Go to: https://vercel.com/dashboard
2. Click your backend project
3. Settings → General
4. Scroll to **"Build & Development Settings"**
5. Clear build cache
6. Redeploy

### Or Force Redeploy

```bash
# Make an empty commit to trigger redeploy
git commit --allow-empty -m "Force Vercel redeploy with fixed dependencies"
git push origin main
```

### Check Build Logs

The issue is Vercel is using old commit. In Vercel:
1. Go to latest deployment
2. Check "Source" - should be commit `02d593a`
3. If not, trigger manual redeploy

---

## 📦 Docker Files Ready

Your project already has:
- ✅ `frontend/Dockerfile` - Frontend container
- ✅ `backend/Dockerfile` - Backend container
- ✅ `docker-compose.yml` - Development setup
- ✅ `docker-compose.prod.yml` - Production setup (just created)

---

## 🎯 Recommended Deployment

**For your use case, I recommend Railway.app:**

1. **Easy setup** - 5 minutes
2. **Free tier** - $5 credit/month
3. **Auto-deploys** from GitHub
4. **Better for Python** apps than Vercel
5. **Works well with Supabase**

**Quick Start:**
1. Go to: https://railway.app/
2. Sign in with GitHub
3. Deploy → From GitHub
4. Add environment variables
5. Done!

---

## 🐛 Troubleshooting

### Docker Build Fails

```bash
# Clear Docker cache
docker system prune -a

# Rebuild
docker-compose -f docker-compose.prod.yml build --no-cache
```

### Port Already in Use

```bash
# Kill process on port
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Environment Variables Not Working

Make sure `.env` file is in project root with all variables set.

---

## ✅ Success Checklist

- [ ] Chose deployment platform
- [ ] Pushed code to GitHub
- [ ] Created new OpenAI API key
- [ ] Added all environment variables
- [ ] Deployed application
- [ ] Tested health endpoint
- [ ] Tested full application
- [ ] Updated frontend API URL

---

**Recommended:** Use Railway.app or Render.com for easiest deployment!
