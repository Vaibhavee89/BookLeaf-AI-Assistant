# 🚀 Quick Setup: Cloudflare Worker Proxy

Use this guide to deploy a Cloudflare Worker that proxies your Supabase requests, bypassing regional connectivity issues.

## Why This Helps

Your Supabase instance is unreachable from your region, but it might be accessible from Cloudflare's global edge network. This worker acts as a middleman:

```
Your App → Cloudflare Worker → Supabase
(Your Region) → (Global Edge) → (Supabase Region)
```

## ⚡ Quick Start (5 minutes)

### Step 1: Install Wrangler CLI

```bash
npm install -g wrangler
```

### Step 2: Run the Setup Script

```bash
cd cloudflare-worker
./setup.sh
```

This will:
- ✅ Check if you're logged in to Cloudflare
- ✅ Deploy the worker
- ✅ Give you the worker URL

### Step 3: Update Your Backend

Copy the worker URL from the deployment output (looks like):
```
https://bookleaf-supabase-proxy.YOUR-USERNAME.workers.dev
```

Update `backend/.env`:
```bash
# OLD (direct connection - not working)
# SUPABASE_URL=https://frpjbfuslgsirqdjdczy.supabase.co

# NEW (via Cloudflare Worker)
SUPABASE_URL=https://bookleaf-supabase-proxy.YOUR-USERNAME.workers.dev
```

Also update the root `.env` file:
```bash
SUPABASE_URL=https://bookleaf-supabase-proxy.YOUR-USERNAME.workers.dev
```

### Step 4: Restart Your Backend

```bash
docker-compose restart backend
```

### Step 5: Test It!

```bash
# Test the worker directly
curl https://bookleaf-supabase-proxy.YOUR-USERNAME.workers.dev/health

# Should return:
# {"status":"healthy","service":"supabase-proxy","timestamp":"2024-..."}
```

### Step 6: Seed Your Database

Now that Supabase is accessible via the proxy:

```bash
# Seed mock authors
docker-compose exec backend bash -c "echo 'n' | python scripts/seed_data.py"

# Generate knowledge base embeddings
docker-compose exec backend python scripts/prepare_knowledge_base.py
```

## 🔧 Manual Setup (if script doesn't work)

### 1. Login to Cloudflare

```bash
wrangler login
```

### 2. Deploy the Worker

```bash
cd cloudflare-worker
wrangler deploy
```

### 3. Copy the URL

Look for output like:
```
✨  Built successfully!
🌎  Deploying...
✨  Success! Deployed to https://bookleaf-supabase-proxy.YOUR-USERNAME.workers.dev
```

### 4. Update Environment Variables

```bash
# Edit backend/.env
nano backend/.env

# Change SUPABASE_URL to your worker URL
# Save and exit (Ctrl+X, Y, Enter)
```

### 5. Restart Backend

```bash
docker-compose restart backend
```

## 🧪 Testing

### Test Worker Health

```bash
curl https://YOUR-WORKER-URL/health
```

### Test Supabase Proxy

```bash
curl https://YOUR-WORKER-URL/rest/v1/ \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZycGpiZnVzbGdzaXJnZGpkY3p5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIxOTA5MzAsImV4cCI6MjA4Nzc2NjkzMH0.KrO7CgANZp6BwBMfxxbVaOozddPlGCtZ0EFFql8cFYc"
```

Should return Supabase API response.

### Test from Backend

```bash
# Check backend logs
docker-compose logs backend

# Should see successful Supabase connections
```

## 📊 Monitor Your Worker

### View Logs in Real-Time

```bash
cd cloudflare-worker
wrangler tail
```

### View Metrics

Visit: https://dash.cloudflare.com → Workers & Pages → Select your worker

You'll see:
- Request count
- Success rate
- Errors
- CPU time usage

## 🔒 Security Notes

**Current Setup**: The worker allows requests from localhost (for development).

**For Production**:
1. Update `ALLOWED_ORIGINS` in `worker.js`
2. Add authentication if needed
3. Set up rate limiting

See `cloudflare-worker/README.md` for details.

## 💰 Cost

**Free Tier** (plenty for development):
- 100,000 requests/day
- Unlimited bandwidth

**If you exceed free tier**:
- $5/month for Workers Paid plan
- Includes 10 million requests/month

## ❓ Troubleshooting

### Worker Deployed but Still Can't Connect?

Check if Supabase is completely down:
- Visit: https://status.supabase.com
- If there's a global outage, even the proxy won't help

### "Unauthorized" or "Invalid API Key"?

Make sure you're passing the correct headers:
```bash
-H "apikey: YOUR_SUPABASE_ANON_KEY"
-H "Authorization: Bearer YOUR_SUPABASE_ANON_KEY"
```

### CORS Errors in Frontend?

Add your frontend URL to `ALLOWED_ORIGINS` in `worker.js`:
```javascript
const ALLOWED_ORIGINS = [
  'http://localhost:3000',
  'http://localhost:8000',
  'https://your-production-domain.com'  // Add this
];
```

Then redeploy:
```bash
wrangler deploy
```

### Worker URL Not Working?

Test locally first:
```bash
cd cloudflare-worker
wrangler dev

# In another terminal:
curl http://localhost:8787/health
```

## 🎯 Next Steps After Setup

Once your worker is working:

1. ✅ Seed database with mock authors
2. ✅ Generate knowledge base embeddings
3. ✅ Test the full application at http://localhost:3000
4. ✅ Try sample queries

## 📚 Additional Resources

- **Detailed Guide**: `cloudflare-worker/README.md`
- **Cloudflare Workers Docs**: https://developers.cloudflare.com/workers/
- **Wrangler CLI Docs**: https://developers.cloudflare.com/workers/wrangler/

---

**Need help?** Check the logs:
```bash
# Worker logs
wrangler tail

# Backend logs
docker-compose logs -f backend
```
