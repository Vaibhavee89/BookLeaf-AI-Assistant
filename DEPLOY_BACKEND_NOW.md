# 🚀 Deploy Backend to Vercel (With Supabase)

Your backend is ready to deploy! Follow these steps carefully.

---

## 🔐 BEFORE YOU START

### ⚠️ CRITICAL: Get a NEW OpenAI API Key

Your current key was exposed. Get a new one:

1. **Go to:** https://platform.openai.com/api-keys
2. **Revoke** your old key: `sk-proj-CSLXloalKMiuXgYWWQ4...`
3. **Create** a new key
4. **Copy** it - you'll need it in Step 3

---

## 📋 Step-by-Step Deployment

### Step 1: Go to Vercel (30 seconds)

**Open:** https://vercel.com/new

### Step 2: Import Your Repository (1 minute)

1. Click **"Import Git Repository"**
2. Find and select: **Vaibhavee89/BookLeaf-AI-Assistant**
3. Click **"Import"**

### Step 3: Configure Project (3 minutes)

#### Project Settings:

- **Project Name:** `bookleaf-api` (or any name you prefer)
- **Framework Preset:** Other
- **Root Directory:** **`backend`** ← **VERY IMPORTANT!**

Click the **"Edit"** button next to "Root Directory" and type: `backend`

#### Build Settings:

Leave as default - Vercel will auto-detect.

### Step 4: Add Environment Variables (2 minutes)

Click **"Environment Variables"** section and add these **one by one**:

#### Required Variables:

```env
OPENAI_API_KEY=sk-proj-YOUR-NEW-KEY-HERE
```
**⚠️ Use your NEW key from Step 1!**

```env
SUPABASE_URL=https://frpjbfuslgsirgdjdczy.supabase.co
```

```env
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZycGpiZnVzbGdzaXJnZGpkY3p5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIxOTA5MzAsImV4cCI6MjA4Nzc2NjkzMH0.KrO7CgANZp6BwBMfxxbVaOozddPlGCtZ0EFFql8cFYc
```

```env
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZycGpiZnVzbGdzaXJnZGpkY3p5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjE5MDkzMCwiZXhwIjoyMDg3NzY2OTMwfQ.M8uF897ySJce31EC7feCsRFxeZLEtitER1jzl0qmyL0
```

#### Optional but Recommended:

```env
ENVIRONMENT=production
DEBUG=false
PRIMARY_MODEL=gpt-4-turbo-preview
CLASSIFICATION_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-large
APP_NAME=BookLeaf AI Assistant
LOG_LEVEL=INFO
```

**How to add each variable:**
1. Type the **name** (e.g., `OPENAI_API_KEY`)
2. Type the **value**
3. Click **"Add"**
4. Repeat for each variable

### Step 5: Deploy! (1 minute)

Click the big **"Deploy"** button at the bottom.

⏱️ Wait 2-5 minutes for deployment to complete.

---

## ✅ After Deployment

### Your Backend URL

After deployment succeeds, you'll get a URL like:
```
https://bookleaf-api.vercel.app
```

**Copy this URL!** You'll need it for the next step.

### Test Your Backend

Open in browser:
```
https://your-backend-url.vercel.app/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0"
}
```

If you see this, **your backend is working!** ✅

### Test Supabase Connection

```
https://your-backend-url.vercel.app/docs
```

This should show the API documentation.

---

## 🔗 Connect Frontend to Backend

### Step 6: Update Frontend Environment Variable

1. **Go to Vercel Dashboard:** https://vercel.com/dashboard
2. **Click on your FRONTEND project** (not the backend)
3. **Go to:** Settings → Environment Variables
4. **Find:** `NEXT_PUBLIC_API_URL`
5. **Update value to:** `https://your-backend-url.vercel.app`
6. **Click "Save"**

### Step 7: Redeploy Frontend

1. Stay in your frontend project
2. Go to **"Deployments"** tab
3. Click **"..."** on latest deployment
4. Click **"Redeploy"**

Or trigger via Git:
```bash
git commit --allow-empty -m "Update API URL"
git push origin main
```

---

## 🎉 You're Done!

Your full-stack application is now deployed:

- **Frontend:** https://your-frontend.vercel.app
- **Backend:** https://your-backend.vercel.app
- **Database:** Supabase (hosted)

### Test the Complete App

1. Open your frontend URL
2. Try the chat interface
3. It should now connect to your backend
4. Backend connects to Supabase
5. Everything works! 🚀

---

## 🐛 Troubleshooting

### Backend Deployment Fails

**Check:**
1. Root Directory is set to `backend`
2. All environment variables are added
3. OpenAI API key is valid

**View logs:**
- Go to Deployments tab
- Click on failed deployment
- Read the build logs

### Backend 500 Error

**Likely causes:**
1. Missing environment variable
2. Invalid OpenAI API key
3. Supabase connection issue

**Check logs:**
```
Vercel Dashboard → Your Backend Project → Deployments → Function Logs
```

### Frontend Can't Connect

**Check:**
1. `NEXT_PUBLIC_API_URL` is correct
2. Backend URL is accessible
3. CORS is enabled (should be automatic)

### Supabase Connection Error

**Verify:**
1. Supabase project is active (not paused)
2. VPN is not needed for Vercel (Vercel can reach Supabase directly)
3. Supabase credentials are correct

---

## 📞 Quick Support

- **Vercel Status:** https://www.vercel-status.com
- **Supabase Status:** https://status.supabase.com
- **View Logs:** Vercel Dashboard → Deployments → Function Logs

---

## ✅ Deployment Checklist

- [ ] Created new OpenAI API key
- [ ] Went to https://vercel.com/new
- [ ] Imported BookLeaf-AI-Assistant repo
- [ ] Set Root Directory to `backend`
- [ ] Added all environment variables
- [ ] Deployed backend
- [ ] Got backend URL
- [ ] Tested `/health` endpoint
- [ ] Updated frontend `NEXT_PUBLIC_API_URL`
- [ ] Redeployed frontend
- [ ] Tested full application

---

**Ready? Start here:** https://vercel.com/new

**Estimated Time:** 10 minutes total
