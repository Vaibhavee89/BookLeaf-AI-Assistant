# 🚀 Deploy Your Project NOW!

Your project is on GitHub: **https://github.com/Vaibhavee89/BookLeaf-AI-Assistant**

## Method 1: Vercel Dashboard (Easiest - 5 minutes)

### Step 1: Import to Vercel (2 minutes)

1. **Go to:** https://vercel.com/new
2. **Login** with GitHub (if not already logged in)
3. **Import** your repository:
   - Click "Import Git Repository"
   - Select: **Vaibhavee89/BookLeaf-AI-Assistant**
   - Click "Import"

### Step 2: Configure Frontend (2 minutes)

**Framework Preset:** Next.js (auto-detected)
**Root Directory:** `frontend`
**Build Command:** `npm run build`
**Output Directory:** `.next`
**Install Command:** `npm install`

### Step 3: Add Environment Variables (1 minute)

Click "Environment Variables" and add:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.vercel.app
NEXT_PUBLIC_APP_NAME=BookLeaf AI Assistant
```

**Note:** You'll update `NEXT_PUBLIC_API_URL` after deploying the backend.

### Step 4: Deploy!

Click **"Deploy"** and wait 2-3 minutes.

Your frontend will be live at: `https://bookleaf-ai-assistant.vercel.app`

---

## Method 2: Deploy Backend Separately (Optional)

### Step 1: Create New Vercel Project

1. Go to: https://vercel.com/new
2. Import the same repository again
3. **Root Directory:** `backend`

### Step 2: Add Backend Environment Variables

```env
OPENAI_API_KEY=sk-proj-YOUR-NEW-KEY-HERE
SUPABASE_URL=https://frpjbfuslgsirgdjdczy.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZycGpiZnVzbGdzaXJnZGpkY3p5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIxOTA5MzAsImV4cCI6MjA4Nzc2NjkzMH0.KrO7CgANZp6BwBMfxxbVaOozddPlGCtZ0EFFql8cFYc
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZycGpiZnVzbGdzaXJnZGpkY3p5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjE5MDkzMCwiZXhwIjoyMDg3NzY2OTMwfQ.M8uF897ySJce31EC7feCsRFxeZLEtitER1jzl0qmyL0
ENVIRONMENT=production
DEBUG=false
```

**CRITICAL:** Replace `OPENAI_API_KEY` with a NEW key from: https://platform.openai.com/api-keys

### Step 3: Deploy Backend

Click **"Deploy"**

Your backend will be at: `https://bookleaf-api.vercel.app`

### Step 4: Update Frontend Environment

Go back to your frontend project → Settings → Environment Variables

Update:
```env
NEXT_PUBLIC_API_URL=https://bookleaf-api.vercel.app
```

Redeploy frontend.

---

## ⚡ Quick Links

- **Your GitHub Repo:** https://github.com/Vaibhavee89/BookLeaf-AI-Assistant
- **Vercel Dashboard:** https://vercel.com/dashboard
- **Deploy New:** https://vercel.com/new

---

## ✅ After Deployment

Test your app:

1. **Frontend:** https://your-app.vercel.app
2. **Backend Health:** https://your-api.vercel.app/health
3. **API Docs:** https://your-api.vercel.app/docs

---

## 🔐 IMPORTANT: Security

⚠️ **Before deploying, ROTATE your OpenAI API key:**

1. Go to: https://platform.openai.com/api-keys
2. Revoke old key
3. Create new key
4. Use new key in Vercel environment variables

The old key was exposed in our conversation!

---

## 🆘 Need Help?

- Full Guide: `VERCEL_DEPLOYMENT_GUIDE.md`
- Checklist: `DEPLOYMENT_CHECKLIST.md`
- Vercel Docs: https://vercel.com/docs

---

**Ready? Start here:** https://vercel.com/new

**Estimated Time:** 5-10 minutes total
