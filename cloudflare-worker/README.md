# Cloudflare Worker - Supabase Proxy

This Cloudflare Worker acts as a proxy for Supabase requests, routing traffic through Cloudflare's global edge network. This can help bypass regional connectivity issues.

## Why Use This?

- **Better Connectivity**: Routes requests through Cloudflare's global network
- **Regional Issues**: Bypasses local ISP or regional connectivity problems
- **Caching**: Can add caching layers (optional)
- **Free Tier**: 100,000 requests/day on Cloudflare's free plan

## Prerequisites

1. **Cloudflare Account**: Sign up at https://dash.cloudflare.com/sign-up
2. **Node.js**: Install from https://nodejs.org (v16 or higher)
3. **Wrangler CLI**: Cloudflare's command-line tool

## Quick Setup

### 1. Install Wrangler CLI

```bash
npm install -g wrangler
```

### 2. Login to Cloudflare

```bash
wrangler login
```

This will open a browser window to authenticate with Cloudflare.

### 3. Deploy the Worker

```bash
cd /Users/vaibhavee/project/Bookleaf_Assignment/cloudflare-worker
wrangler deploy
```

The deployment will output a URL like:
```
https://bookleaf-supabase-proxy.YOUR-USERNAME.workers.dev
```

### 4. Test the Worker

```bash
# Health check
curl https://bookleaf-supabase-proxy.YOUR-USERNAME.workers.dev/health

# Test Supabase proxy
curl https://bookleaf-supabase-proxy.YOUR-USERNAME.workers.dev/rest/v1/ \
  -H "apikey: YOUR_SUPABASE_ANON_KEY"
```

## Update Your Backend to Use the Proxy

### Option 1: Update Environment Variables

Edit `backend/.env`:

```bash
# Replace the Supabase URL with your Worker URL
SUPABASE_URL=https://bookleaf-supabase-proxy.YOUR-USERNAME.workers.dev
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Option 2: Update Docker Compose

Edit `docker-compose.yml`:

```yaml
environment:
  - SUPABASE_URL=https://bookleaf-supabase-proxy.YOUR-USERNAME.workers.dev
```

Then restart:
```bash
docker-compose restart backend
```

## Advanced Configuration

### Add Custom Domain

1. **Add a Route** in `wrangler.toml`:
   ```toml
   routes = [
     { pattern = "supabase-proxy.your-domain.com/*", zone_name = "your-domain.com" }
   ]
   ```

2. **Deploy**:
   ```bash
   wrangler deploy
   ```

### Add Caching (Optional)

Add to `worker.js` before returning the response:

```javascript
// Add cache headers for GET requests
if (request.method === 'GET') {
  const cacheHeaders = new Headers(response.headers);
  cacheHeaders.set('Cache-Control', 'public, max-age=60');

  return new Response(response.body, {
    status: response.status,
    headers: cacheHeaders
  });
}
```

### Add Rate Limiting (Optional)

Use Cloudflare Workers KV for rate limiting:

```javascript
// In wrangler.toml, add:
# [[kv_namespaces]]
# binding = "RATE_LIMIT"
# id = "your-kv-namespace-id"

// In worker.js:
const rateLimitKey = `rate-limit:${clientIP}`;
const count = await env.RATE_LIMIT.get(rateLimitKey);
if (count && parseInt(count) > 100) {
  return new Response('Rate limit exceeded', { status: 429 });
}
```

## Monitoring

### View Logs

```bash
wrangler tail
```

### Check Metrics

Visit: https://dash.cloudflare.com/YOUR-ACCOUNT-ID/workers/services/view/bookleaf-supabase-proxy

### Debug Issues

```bash
# Test locally before deploying
wrangler dev

# Then test with:
curl http://localhost:8787/health
```

## Security Considerations

### 1. API Key Protection

The worker currently allows all origins. For production, update `ALLOWED_ORIGINS`:

```javascript
const ALLOWED_ORIGINS = [
  'https://your-production-domain.com',
  'http://localhost:3000'  // Remove in production
];
```

### 2. Add Authentication (Optional)

```javascript
// Add a secret token check
const SECRET_TOKEN = env.PROXY_SECRET;

if (request.headers.get('X-Proxy-Auth') !== SECRET_TOKEN) {
  return new Response('Unauthorized', { status: 401 });
}
```

Add the secret in Cloudflare dashboard or wrangler.toml:
```toml
[env.production.vars]
PROXY_SECRET = "your-secret-token-here"
```

### 3. Use Secrets for Sensitive Data

```bash
# Store secrets securely
wrangler secret put SUPABASE_SERVICE_KEY
# Paste your key when prompted

# Access in worker:
const serviceKey = env.SUPABASE_SERVICE_KEY;
```

## Troubleshooting

### Worker Not Working?

1. **Check Deployment**:
   ```bash
   wrangler deployments list
   ```

2. **View Errors**:
   ```bash
   wrangler tail --format=pretty
   ```

3. **Test Locally**:
   ```bash
   wrangler dev
   ```

### Supabase Still Unreachable?

The worker routes through Cloudflare's network. If Supabase is completely down (not just regionally), the worker won't help.

Check Supabase status: https://status.supabase.com

### CORS Errors?

Make sure your frontend URL is in `ALLOWED_ORIGINS` in `worker.js`.

## Cost Estimate

**Cloudflare Workers Free Tier**:
- 100,000 requests/day
- 10ms CPU time per request
- This is plenty for development and small production apps

**Paid Plan** ($5/month):
- 10 million requests/month included
- $0.50 per additional million

## Alternative: Cloudflare Tunnel

If you want to expose your local Docker containers, use Cloudflare Tunnel:

```bash
# Install cloudflared
brew install cloudflare/cloudflare/cloudflared  # macOS
# or download from: https://github.com/cloudflare/cloudflared/releases

# Login
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create bookleaf

# Configure tunnel (create config.yml)
# Run tunnel
cloudflared tunnel run bookleaf
```

## Next Steps

1. ✅ Deploy the worker
2. ✅ Update your backend environment variables
3. ✅ Restart your Docker containers
4. ✅ Test database seeding

Once the worker is deployed, you can proceed with seeding your database even while Supabase has regional issues!
