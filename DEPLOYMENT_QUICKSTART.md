# 🚀 Quick Deployment to Vercel

Fast track guide to deploy BookLeaf AI Assistant to Vercel.

---

## ⚡ 5-Minute Deployment

### Prerequisites
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login
```

---

## 🎯 Option 1: Deploy Frontend Only (Fastest)

```bash
# Navigate to frontend
cd frontend

# Install dependencies (if not already done)
npm install

# Deploy to Vercel
vercel --prod

# Note the deployment URL
# Update NEXT_PUBLIC_API_URL to point to your backend
```

**Set Environment Variables in Vercel Dashboard:**
- `NEXT_PUBLIC_API_URL` = Your backend URL
- `NEXT_PUBLIC_APP_NAME` = BookLeaf AI Assistant

---

## 🎯 Option 2: Deploy via GitHub (Recommended)

### Step 1: Push to GitHub (2 minutes)

```bash
cd /Users/vaibhavee/project/BookLeaf_Assignment

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/bookleaf-ai.git
git branch -M main
git push -u origin main
```

### Step 2: Import to Vercel (2 minutes)

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your repo
4. Configure:
   - **Root Directory:** `frontend`
   - **Framework:** Next.js (auto-detected)
5. Add environment variables (see below)
6. Click "Deploy"

### Step 3: Environment Variables (1 minute)

Add in Vercel Dashboard → Settings → Environment Variables:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.vercel.app
NEXT_PUBLIC_APP_NAME=BookLeaf AI Assistant

# If deploying backend too:
OPENAI_API_KEY=your-key-here
SUPABASE_URL=https://frpjbfuslgsirgdjdczy.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key
```

---

## 🔧 Deploy Backend (Optional - If Needed)

```bash
cd backend

# Install mangum for serverless
pip install mangum
pip freeze > requirements-vercel.txt

# Deploy
vercel --prod
```

---

## ✅ Verify Deployment

```bash
# Test frontend
curl https://your-app.vercel.app

# Test backend API
curl https://your-api.vercel.app/health
```

---

## 🎉 Done!

Your app is live at: `https://your-app.vercel.app`

**Next Steps:**
- Configure custom domain (optional)
- Set up monitoring
- Enable analytics

**Full Guide:** See `VERCEL_DEPLOYMENT_GUIDE.md`

---

## 🔐 Security Reminder

⚠️ **IMPORTANT:** Rotate your OpenAI API key!
- Current key was exposed in this conversation
- Go to: https://platform.openai.com/api-keys
- Revoke old key and create new one
- Update in Vercel environment variables

---

## 🆘 Quick Troubleshooting

**Build fails?**
```bash
# Check dependencies
cd frontend && npm install
cd backend && pip install -r requirements-vercel.txt
```

**API not working?**
- Check environment variables in Vercel dashboard
- Verify Supabase connection
- Review deployment logs: `vercel logs`

**CORS error?**
- Update CORS settings in `backend/app/main.py`
- Add your frontend URL to allowed origins

---

**Questions?** See full guide: `VERCEL_DEPLOYMENT_GUIDE.md`
