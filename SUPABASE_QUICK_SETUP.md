# Supabase Quick Setup (5 minutes)

## 1. Create Project

1. Go to: https://supabase.com
2. Click "Start your project" or "New Project"
3. Sign in with GitHub (recommended) or email
4. Click "New Project"
5. Fill in:
   - **Name**: `bookleaf-ai-assistant`
   - **Database Password**: Create a strong password (SAVE THIS!)
   - **Region**: Choose closest to you (e.g., US West, US East, Europe, etc.)
   - **Pricing Plan**: Free (sufficient for this project)
6. Click "Create new project"
7. ⏳ Wait 2-3 minutes for project to provision

## 2. Enable pgvector Extension

Once your project is ready:

1. Click on **"SQL Editor"** in left sidebar (icon looks like `</>`)
2. Click **"+ New query"**
3. Copy and paste this SQL:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. Click **"Run"** or press `Ctrl+Enter` (Mac: `Cmd+Enter`)
5. You should see: ✅ Success (or "extension already exists")

## 3. Run Database Schema

Still in SQL Editor:

1. Click **"+ New query"**
2. Open the file: `database/schema.sql` from this project
3. Copy ALL the contents
4. Paste into the SQL Editor
5. Click **"Run"** or press `Ctrl+Enter`
6. ⏳ Wait ~10 seconds
7. You should see: ✅ Success messages

## 4. Get Your API Keys

1. Click **"Settings"** in left sidebar (gear icon at bottom)
2. Click **"API"** in the settings menu
3. You'll see two sections:

### Project URL
- Copy the URL (looks like: `https://xxxxxxxxxxxxx.supabase.co`)
- **Save this as: SUPABASE_URL**

### Project API keys

Find these two keys:

**anon / public key**:
- This is already visible
- Copy it
- **Save this as: SUPABASE_KEY**

**service_role key**:
- Click "Reveal" next to it
- Copy it (⚠️ Keep this secret!)
- **Save this as: SUPABASE_SERVICE_ROLE_KEY**

## 5. Verify Tables Created

1. Click **"Table Editor"** in left sidebar
2. You should see 8 tables:
   - authors
   - conversations
   - escalations
   - identities
   - knowledge_documents
   - knowledge_embeddings
   - messages
   - query_analytics

If you see all 8 tables: ✅ **You're done with Supabase!**

---

## Quick Reference

After setup, you should have:
- ✅ Supabase project created
- ✅ pgvector extension enabled
- ✅ 8 tables created
- ✅ 3 API keys copied:
  1. SUPABASE_URL
  2. SUPABASE_KEY (anon/public)
  3. SUPABASE_SERVICE_ROLE_KEY (secret!)
