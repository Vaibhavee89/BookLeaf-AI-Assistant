# BookLeaf AI Assistant - Vercel Deployment Guide

This guide will help you deploy the BookLeaf AI Assistant (Next.js frontend + FastAPI backend) to Vercel.

---

## 🏗️ Architecture

**Deployment Strategy:**
- **Frontend:** Next.js app (native Vercel support)
- **Backend:** FastAPI as Vercel Serverless Functions (Python runtime)
- **Database:** Supabase (hosted, no deployment needed)

---

## 📋 Prerequisites

1. **Vercel Account**
   - Sign up at: https://vercel.com/signup
   - Install Vercel CLI: `npm install -g vercel`

2. **GitHub Repository** (Recommended)
   - Push your code to GitHub
   - Connect to Vercel for automatic deployments

3. **Environment Variables Ready**
   - OpenAI API Key
   - Supabase URL and Keys

---

## 🚀 Deployment Options

### Option 1: Deploy via GitHub (Recommended)

#### Step 1: Push to GitHub

```bash
cd /Users/vaibhavee/project/BookLeaf_Assignment

# Initialize git if not already done
git init

# Create .gitignore if needed
cat > .gitignore << 'EOF'
# Environment variables
.env
.env.local
*.env

# Node modules
node_modules/
frontend/node_modules/

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
backend/venv/

# Build outputs
.next/
dist/
build/

# OS files
.DS_Store
EOF

# Add and commit
git add .
git commit -m "Initial commit for Vercel deployment"

# Create GitHub repo and push
# (Create repo on GitHub first: https://github.com/new)
git remote add origin https://github.com/YOUR_USERNAME/bookleaf-ai.git
git branch -M main
git push -u origin main
```

#### Step 2: Import to Vercel

1. Go to: https://vercel.com/new
2. Click **"Import Git Repository"**
3. Select your GitHub repository
4. Configure project:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend` (for frontend deployment)
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
   - **Install Command:** `npm install`

#### Step 3: Configure Environment Variables

In Vercel dashboard, add these environment variables:

**For Frontend:**
```
NEXT_PUBLIC_API_URL=https://your-project.vercel.app/api
NEXT_PUBLIC_APP_NAME=BookLeaf AI Assistant
```

**For Backend (API Routes):**
```
OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE
SUPABASE_URL=https://frpjbfuslgsirgdjdczy.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
PRIMARY_MODEL=gpt-4-turbo-preview
CLASSIFICATION_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-large
ENVIRONMENT=production
DEBUG=false
```

#### Step 4: Deploy

Click **"Deploy"** and wait for the build to complete!

---

### Option 2: Deploy via Vercel CLI

#### Step 1: Login to Vercel

```bash
vercel login
```

#### Step 2: Deploy Frontend

```bash
cd frontend

# First deployment (follow prompts)
vercel

# Production deployment
vercel --prod
```

#### Step 3: Deploy Backend as API Routes

```bash
cd ../backend

# Create Vercel project
vercel

# Production deployment
vercel --prod
```

#### Step 4: Link Frontend to Backend

Update frontend environment variables with the backend API URL.

---

## 🔧 Project Structure for Vercel

Your project should have this structure:

```
BookLeaf_Assignment/
├── frontend/                 # Next.js app
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── next.config.js
│   └── .env.local.example
├── backend/                  # FastAPI app
│   ├── app/
│   ├── api/
│   │   └── index.py         # Vercel serverless entry point
│   ├── requirements-vercel.txt
│   └── vercel.json
├── vercel.json               # Monorepo config (optional)
└── VERCEL_DEPLOYMENT_GUIDE.md
```

---

## 🔐 Security Checklist

Before deploying, ensure:

- [ ] **API Keys:** Never commit `.env` files to Git
- [ ] **Environment Variables:** Set all secrets in Vercel dashboard
- [ ] **CORS:** Configure allowed origins in backend
- [ ] **OpenAI Key:** Rotate if exposed in conversation history
- [ ] **Supabase RLS:** Enable Row Level Security policies
- [ ] **Rate Limiting:** Implement rate limiting for API endpoints

---

## 🎯 Deployment Strategies

### Strategy 1: Monorepo (Single Deployment)

Deploy both frontend and backend from one repository using the root `vercel.json`.

**Pros:** Simplified management, single deployment
**Cons:** Longer build times

### Strategy 2: Separate Deployments (Recommended)

Deploy frontend and backend as separate Vercel projects.

**Frontend Deployment:**
```bash
cd frontend
vercel --prod
```

**Backend Deployment:**
```bash
cd backend
vercel --prod
```

**Pros:** Faster builds, independent scaling
**Cons:** Need to manage two projects

---

## 🔄 Backend Adaptation for Vercel

### Install Mangum (Serverless Adapter)

```bash
cd backend
source venv/bin/activate
pip install mangum
pip freeze > requirements-vercel.txt
```

### Create Serverless Entry Point

The `backend/api/index.py` file wraps your FastAPI app:

```python
from mangum import Mangum
from app.main import app

handler = Mangum(app)
```

### Configure Backend for Vercel

Create `backend/vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

---

## 🌐 Custom Domain Setup

### Option 1: Vercel Domain

After deployment, Vercel provides:
- `your-project.vercel.app` (auto-assigned)

### Option 2: Custom Domain

1. Go to **Project Settings → Domains**
2. Add your custom domain: `bookleaf.yourdomain.com`
3. Configure DNS records as instructed by Vercel
4. Update environment variables with new domain

---

## 🧪 Testing Deployment

### Test Frontend

```bash
curl https://your-project.vercel.app
```

### Test Backend API

```bash
# Health check
curl https://your-project.vercel.app/api/health

# Identity resolution
curl -X POST https://your-project.vercel.app/api/v1/identity/resolve \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### Test via Browser

1. Open: https://your-project.vercel.app
2. Navigate through the UI
3. Test chat functionality
4. Check console for errors

---

## 🐛 Troubleshooting

### Issue 1: Build Fails - Missing Dependencies

**Error:**
```
Error: Cannot find module 'xyz'
```

**Solution:**
```bash
# For frontend
cd frontend
npm install xyz --save

# For backend
cd backend
pip install xyz
pip freeze > requirements-vercel.txt
```

### Issue 2: API Returns 500 Error

**Cause:** Environment variables not set

**Solution:**
1. Go to Vercel Dashboard → Project Settings → Environment Variables
2. Add all required variables
3. Redeploy: `vercel --prod`

### Issue 3: CORS Error

**Error:**
```
Access to fetch blocked by CORS policy
```

**Solution:**

Update `backend/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 4: Cold Start Delays

**Symptom:** First request is slow (5-10 seconds)

**Explanation:** Serverless functions have cold starts

**Mitigation:**
- Use Vercel Pro for faster cold starts
- Implement request warming
- Consider dedicated backend hosting for high traffic

### Issue 5: Database Connection Issues

**Error:**
```
Could not connect to Supabase
```

**Solution:**
1. Verify Supabase URL and keys in environment variables
2. Check Supabase project is active (not paused)
3. Ensure VPN/proxy settings if needed
4. Test connection from Vercel CLI:

```bash
vercel env pull
vercel dev
```

---

## 📊 Monitoring & Analytics

### Enable Vercel Analytics

1. Go to Project Settings → Analytics
2. Enable Web Analytics
3. Monitor:
   - Page views
   - Performance metrics
   - API response times
   - Error rates

### Log Viewing

```bash
# View deployment logs
vercel logs

# View function logs
vercel logs --since 1h
```

### Performance Monitoring

- **Vercel Dashboard:** Real-time metrics
- **Supabase Dashboard:** Database performance
- **OpenAI Dashboard:** API usage and costs

---

## 💰 Cost Considerations

### Vercel Pricing

**Free Tier Includes:**
- 100 GB bandwidth
- 100 hours serverless execution
- Automatic HTTPS
- Unlimited deployments

**Pro Tier ($20/month):**
- 1 TB bandwidth
- 1000 hours serverless execution
- Advanced analytics
- Password protection

### Optimization Tips

1. **Static Generation:** Use Next.js SSG where possible
2. **Edge Caching:** Cache API responses
3. **Optimize Images:** Use Next.js Image component
4. **API Rate Limiting:** Prevent abuse

---

## 🔄 Continuous Deployment

### Automatic Deployments

Vercel automatically deploys when you push to GitHub:

- **Push to `main`:** Deploys to production
- **Push to other branches:** Creates preview deployments
- **Pull Requests:** Creates preview URLs

### Manual Deployment

```bash
# Preview deployment
vercel

# Production deployment
vercel --prod

# Rollback to previous deployment
vercel rollback
```

---

## 📝 Post-Deployment Checklist

After successful deployment:

- [ ] Test all API endpoints
- [ ] Verify database connections
- [ ] Test user authentication flow
- [ ] Check identity resolution
- [ ] Test chat functionality
- [ ] Verify analytics tracking
- [ ] Set up monitoring alerts
- [ ] Document deployment URL
- [ ] Update README with live URL
- [ ] Test on mobile devices
- [ ] Run security audit
- [ ] Enable SSL/HTTPS
- [ ] Configure custom domain (optional)
- [ ] Set up staging environment

---

## 🚨 Important Notes

### OpenAI API Key Security

⚠️ **Your OpenAI API key from the conversation should be rotated!**

1. Go to: https://platform.openai.com/api-keys
2. Revoke the current key
3. Create a new key
4. Update in Vercel environment variables

### Supabase Considerations

- Ensure your Supabase project is on a paid plan for production
- Enable Row Level Security (RLS) policies
- Set up database backups
- Monitor database usage

### Environment-Specific Settings

**Development:**
```env
DEBUG=true
ENVIRONMENT=development
```

**Production:**
```env
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

---

## 📚 Additional Resources

- **Vercel Documentation:** https://vercel.com/docs
- **Next.js Deployment:** https://nextjs.org/docs/deployment
- **FastAPI on Vercel:** https://vercel.com/docs/functions/serverless-functions/runtimes/python
- **Mangum Documentation:** https://mangum.io/
- **Supabase Docs:** https://supabase.com/docs

---

## 🎉 Quick Start Command

```bash
# One-command deployment (from project root)
cd frontend && vercel --prod

# Get deployment URL
vercel ls
```

---

## 📞 Support

If you encounter issues:

1. Check Vercel deployment logs
2. Review environment variables
3. Test locally with `vercel dev`
4. Check Supabase connection
5. Verify API keys are valid

---

**Last Updated:** 2026-02-28
**Version:** 1.0.0
