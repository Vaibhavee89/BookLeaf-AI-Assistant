# 🚂 Railway Deployment Guide - Full Stack

Deploy both frontend and backend together on Railway.

---

## 🎯 Quick Setup (5 minutes)

### Step 1: Deploy Backend Service

1. **Go to Railway Dashboard:**
   - https://railway.app/dashboard

2. **New Project:**
   - Click **"New Project"**
   - Select **"Deploy from GitHub repo"**
   - Choose: **`Vaibhavee89/BookLeaf-AI-Assistant`**

3. **Configure Backend Service:**
   - Railway will detect the repo
   - Click **"Add variables"** and add:

   ```
   OPENAI_API_KEY=your-openai-api-key-here
   SUPABASE_URL=https://bookleaf-supabase-proxy.vaibhaveesingh89.workers.dev
   SUPABASE_KEY=your-supabase-anon-key-here
   SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key-here
   ENVIRONMENT=production
   DEBUG=false
   PRIMARY_MODEL=gpt-4-turbo-preview
   CLASSIFICATION_MODEL=gpt-4o-mini
   EMBEDDING_MODEL=text-embedding-3-large
   ```

   **Note:** Get your actual keys from your `.env` file or from the respective service dashboards.

4. **Set Root Directory:**
   - Click **"Settings"**
   - Set **"Root Directory"** to: `backend`
   - Set **"Start Command"** to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Deploy Backend:**
   - Click **"Deploy"**
   - Wait 2-3 minutes
   - Copy the **backend URL** (e.g., `https://bookleaf-backend.up.railway.app`)

---

### Step 2: Deploy Frontend Service

1. **In the same Railway project:**
   - Click **"New Service"**
   - Select **"GitHub Repo"**
   - Choose: **`Vaibhavee89/BookLeaf-AI-Assistant`** (same repo)

2. **Configure Frontend Service:**
   - Set **"Root Directory"** to: `frontend`
   - Add environment variable:

   ```
   NEXT_PUBLIC_API_URL=https://bookleaf-backend.up.railway.app
   NEXT_PUBLIC_APP_NAME=BookLeaf AI Assistant
   ```

   **IMPORTANT:** Replace `bookleaf-backend.up.railway.app` with YOUR actual backend URL from Step 1.

3. **Deploy Frontend:**
   - Click **"Deploy"**
   - Wait 2-3 minutes
   - You'll get a frontend URL (e.g., `https://bookleaf-frontend.up.railway.app`)

---

## ✅ Verification

### Test Backend:
```bash
curl https://your-backend-url.railway.app/health
```

Should return:
```json
{"status": "healthy"}
```

### Test Frontend:
Open: `https://your-frontend-url.railway.app`

Should see the BookLeaf AI Assistant interface.

---

## 🔧 Configuration Details

### Backend Service Settings:
- **Root Directory:** `backend`
- **Build Command:** Auto-detected (pip install -r requirements.txt)
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Port:** Auto-assigned by Railway ($PORT variable)

### Frontend Service Settings:
- **Root Directory:** `frontend`
- **Build Command:** Auto-detected (npm install && npm run build)
- **Start Command:** `npm start`
- **Port:** Auto-assigned by Railway

---

## 📊 Both Services in One Project

```
Railway Project: BookLeaf-AI-Assistant
│
├── Service 1: Backend (FastAPI)
│   ├── Root: backend/
│   ├── URL: https://bookleaf-backend.up.railway.app
│   └── Port: 8000 (mapped to $PORT)
│
└── Service 2: Frontend (Next.js)
    ├── Root: frontend/
    ├── URL: https://bookleaf-frontend.up.railway.app
    ├── Port: 3000 (mapped to $PORT)
    └── Env: NEXT_PUBLIC_API_URL → Backend URL
```

---

## 🐛 Troubleshooting

### Backend fails with "Field required" error:

**Cause:** Missing environment variables

**Fix:**
1. Go to backend service → Variables tab
2. Verify all required variables are set:
   - `OPENAI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`

### Frontend can't connect to backend:

**Cause:** Wrong `NEXT_PUBLIC_API_URL`

**Fix:**
1. Go to backend service → Settings
2. Copy the **public URL**
3. Go to frontend service → Variables
4. Update `NEXT_PUBLIC_API_URL` with correct backend URL
5. Redeploy frontend

### Supabase connection fails:

**Cause:** Using direct Supabase URL (requires VPN)

**Fix:**
Use Cloudflare Worker proxy instead:
```
SUPABASE_URL=https://bookleaf-supabase-proxy.vaibhaveesingh89.workers.dev
```

---

## 💰 Cost

Railway free tier includes:
- **$5 credit per month**
- Enough for small apps
- Both services can run on free tier

If you need more:
- **Hobby Plan:** $5/month
- **Pro Plan:** $20/month

---

## 🚀 Auto-Deploy on Git Push

Railway automatically redeploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Railway auto-deploys both services!
```

---

## 📝 Summary

✅ Two services in one Railway project
✅ Backend API + Frontend app
✅ Auto-deploy from GitHub
✅ Environment variables configured
✅ Uses Cloudflare Worker proxy for Supabase
✅ Free tier available

---

**Your deployment will be live at:**
- Backend API: `https://bookleaf-backend.up.railway.app`
- Frontend App: `https://bookleaf-frontend.up.railway.app`

🎉 **Done!**
