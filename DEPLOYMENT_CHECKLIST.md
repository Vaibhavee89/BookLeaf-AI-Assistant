# 📋 Vercel Deployment Checklist

Use this checklist to ensure a smooth deployment to Vercel.

---

## Pre-Deployment

### Security
- [ ] **Rotate OpenAI API Key** (exposed in conversation)
  - Go to: https://platform.openai.com/api-keys
  - Revoke old key
  - Create new key
  - Save securely

- [ ] **Verify .gitignore**
  - [ ] `.env` files excluded
  - [ ] `node_modules/` excluded
  - [ ] `venv/` excluded
  - [ ] `.vercel/` excluded

- [ ] **Review Supabase Security**
  - [ ] Row Level Security (RLS) enabled
  - [ ] API keys valid
  - [ ] Database not paused

### Code Preparation
- [ ] **Frontend Ready**
  - [ ] `npm install` runs successfully
  - [ ] `npm run build` completes
  - [ ] No TypeScript errors
  - [ ] Environment variables documented

- [ ] **Backend Ready**
  - [ ] `pip install -r requirements-vercel.txt` works
  - [ ] Mangum installed
  - [ ] `backend/api/index.py` exists
  - [ ] `backend/vercel.json` exists

---

## Deployment Setup

### GitHub (Recommended Path)
- [ ] **Repository Created**
  - [ ] GitHub repo created
  - [ ] Local repo initialized (`git init`)
  - [ ] Files committed
  - [ ] Pushed to GitHub

- [ ] **Vercel Account**
  - [ ] Account created: https://vercel.com
  - [ ] GitHub connected

### Direct Deployment (Alternative)
- [ ] **Vercel CLI Installed**
  ```bash
  npm install -g vercel
  ```

- [ ] **Logged In**
  ```bash
  vercel login
  ```

---

## Vercel Configuration

### Frontend Deployment
- [ ] **Import Project**
  - [ ] Repository imported to Vercel
  - [ ] Framework detected as Next.js
  - [ ] Root directory set to `frontend`

- [ ] **Environment Variables Set**
  - [ ] `NEXT_PUBLIC_API_URL`
  - [ ] `NEXT_PUBLIC_APP_NAME`

- [ ] **Build Settings**
  - [ ] Build Command: `npm run build`
  - [ ] Output Directory: `.next`
  - [ ] Install Command: `npm install`

### Backend Deployment (if separate)
- [ ] **Backend Project Created**
  - [ ] Separate Vercel project
  - [ ] Root directory: `backend`

- [ ] **Environment Variables Set** (All from VERCEL_ENV_TEMPLATE.txt)
  - [ ] `OPENAI_API_KEY` (NEW KEY!)
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_KEY`
  - [ ] `SUPABASE_SERVICE_ROLE_KEY`
  - [ ] `ENVIRONMENT=production`
  - [ ] `DEBUG=false`
  - [ ] `CORS_ORIGINS` (with frontend URL)
  - [ ] All other settings from template

---

## Post-Deployment

### Testing
- [ ] **Frontend Tests**
  - [ ] Site loads: `https://your-app.vercel.app`
  - [ ] No console errors
  - [ ] UI renders correctly
  - [ ] Navigation works

- [ ] **Backend Tests**
  - [ ] Health endpoint: `/health`
    ```bash
    curl https://your-api.vercel.app/health
    ```
  - [ ] Identity resolution works
    ```bash
    curl -X POST https://your-api.vercel.app/api/v1/identity/resolve \
      -H "Content-Type: application/json" \
      -d '{"email": "test@example.com"}'
    ```
  - [ ] No 500 errors

- [ ] **Integration Tests**
  - [ ] Frontend → Backend communication
  - [ ] Database queries work
  - [ ] OpenAI API calls succeed
  - [ ] Error handling works

### Monitoring
- [ ] **Analytics Enabled**
  - [ ] Vercel Analytics activated
  - [ ] Real-time metrics visible

- [ ] **Logs Accessible**
  ```bash
  vercel logs
  ```

- [ ] **Supabase Dashboard**
  - [ ] Query activity visible
  - [ ] No errors in logs

---

## Configuration

### CORS
- [ ] **Update Backend CORS**
  - [ ] Frontend URL added to allowed origins
  - [ ] File: `backend/app/main.py`
  - Code updated:
    ```python
    allow_origins=["https://your-frontend.vercel.app"]
    ```

### Custom Domain (Optional)
- [ ] **Domain Added**
  - [ ] Custom domain configured in Vercel
  - [ ] DNS records updated
  - [ ] SSL certificate active

- [ ] **URLs Updated**
  - [ ] `NEXT_PUBLIC_API_URL` updated
  - [ ] `CORS_ORIGINS` updated
  - [ ] Documentation updated

---

## Production Readiness

### Performance
- [ ] **Optimize Images**
  - [ ] Using Next.js Image component
  - [ ] Images compressed

- [ ] **Edge Caching**
  - [ ] Cache headers configured
  - [ ] Static assets optimized

### Security
- [ ] **HTTPS Enabled** (automatic with Vercel)
- [ ] **Environment Variables Secure**
  - [ ] No secrets in code
  - [ ] All sensitive data in Vercel env vars

- [ ] **Rate Limiting Configured**
  - [ ] API endpoints protected
  - [ ] Abuse prevention in place

### Backup & Recovery
- [ ] **Database Backups**
  - [ ] Supabase automatic backups enabled
  - [ ] Backup schedule confirmed

- [ ] **Deployment History**
  - [ ] Can rollback via Vercel dashboard
  - [ ] Previous deployments accessible

---

## Documentation

- [ ] **README Updated**
  - [ ] Live URL added
  - [ ] Deployment instructions
  - [ ] Environment variables documented

- [ ] **API Documentation**
  - [ ] Swagger/OpenAPI accessible
  - [ ] Endpoints documented

---

## Continuous Deployment

### Auto-Deploy Setup
- [ ] **GitHub Integration**
  - [ ] Push to `main` → production deploy
  - [ ] Pull requests → preview deploys
  - [ ] Branch deploys configured

### Workflow
- [ ] **Development Flow**
  1. Make changes locally
  2. Test locally
  3. Commit to GitHub
  4. Auto-deploy to preview
  5. Merge to main for production

---

## Support & Maintenance

### Monitoring Checklist
- [ ] **Daily:**
  - [ ] Check error logs
  - [ ] Monitor API usage
  - [ ] Review performance metrics

- [ ] **Weekly:**
  - [ ] Review security alerts
  - [ ] Check database usage
  - [ ] Update dependencies

- [ ] **Monthly:**
  - [ ] Review costs
  - [ ] Analyze user metrics
  - [ ] Security audit

### Emergency Contacts
- [ ] **Have Ready:**
  - Vercel support email
  - Supabase support contact
  - OpenAI API status page
  - Team contact information

---

## Final Verification

### Public Access
- [ ] **Test From Different Locations**
  - [ ] Test from mobile
  - [ ] Test from different browsers
  - [ ] Test from different devices

- [ ] **Share With Team**
  - [ ] URL shared
  - [ ] Access tested
  - [ ] Feedback collected

### Success Criteria
- [ ] Site loads in < 3 seconds
- [ ] All API endpoints respond
- [ ] No JavaScript errors
- [ ] Mobile responsive
- [ ] Analytics tracking
- [ ] Error monitoring active

---

## 🎉 Deployment Complete!

### URLs
- **Frontend:** https://_____________________.vercel.app
- **Backend:** https://_____________________.vercel.app
- **Documentation:** https://_____________________.vercel.app/docs

### Next Steps
1. Monitor for 24 hours
2. Gather user feedback
3. Plan next iteration
4. Celebrate! 🎊

---

**Date Deployed:** _______________
**Deployed By:** _______________
**Version:** 1.0.0
