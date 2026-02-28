# Supabase Setup - Step by Step Guide

## Step 1: Create Supabase Account (2 minutes)

### 1.1 Go to Supabase
Open this link in your browser: **https://supabase.com**

### 1.2 Sign Up
- Click **"Start your project"** (green button)
- Sign up with:
  - **GitHub** (recommended - fastest), OR
  - **Email** (will need to verify email)

### 1.3 Verify Email (if using email signup)
- Check your inbox
- Click the verification link
- You'll be redirected back to Supabase

✅ **You should now see the Supabase Dashboard**

---

## Step 2: Create New Project (3 minutes)

### 2.1 Click "New Project"
- You'll see a button that says **"+ New project"**
- Click it

### 2.2 Fill in Project Details

**Organization**:
- If first time: Click "Create organization" and name it (e.g., "My Projects")
- If you have one: Select it from dropdown

**Project Settings**:
```
Name: bookleaf-ai-assistant
Database Password: [Create a STRONG password]
              ⚠️  SAVE THIS PASSWORD SOMEWHERE SAFE!
Region: [Choose closest to you]
        - US West (California)
        - US East (Virginia)
        - Europe (Frankfurt)
        - Asia Pacific (Singapore)
        etc.
Pricing Plan: Free (this is perfect for the project)
```

### 2.3 Create Project
- Click **"Create new project"** (bottom right)
- ⏳ **Wait 2-3 minutes** - Supabase is setting up your database
- You'll see a progress indicator

✅ **When done, you'll see your project dashboard**

---

## Step 3: Enable pgvector Extension (1 minute)

### 3.1 Open SQL Editor
- Look at the **left sidebar**
- Click **"SQL Editor"** (icon looks like `</>`)

### 3.2 Create New Query
- Click **"+ New query"** (top right)

### 3.3 Enable pgvector
Copy and paste this SQL command:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3.4 Run the Query
- Click **"Run"** button (or press Ctrl+Enter / Cmd+Enter)
- You should see: ✅ **Success. No rows returned**

✅ **pgvector extension is now enabled!**

---

## Step 4: Run Database Schema (2 minutes)

### 4.1 Open New Query
- Still in SQL Editor
- Click **"+ New query"** again

### 4.2 Get the Schema File
The schema file is located at: `database/schema.sql` in your project folder.

**On Mac/Linux, you can copy it with:**
```bash
cat /Users/vaibhavee/project/Bookleaf_Assignment/database/schema.sql
```

**Or open it in a text editor and copy all contents**

### 4.3 Paste Schema
- Paste the ENTIRE contents into the SQL Editor
- It should be about 250 lines of SQL

### 4.4 Run the Schema
- Click **"Run"** button
- ⏳ Wait ~10-15 seconds
- You should see multiple success messages

✅ **Database schema created!**

---

## Step 5: Verify Tables Created (30 seconds)

### 5.1 Open Table Editor
- Click **"Table Editor"** in left sidebar (icon looks like a table grid)

### 5.2 Check Tables
You should see **8 tables** in the left panel:
- ✅ authors
- ✅ conversations
- ✅ escalations
- ✅ identities
- ✅ knowledge_documents
- ✅ knowledge_embeddings
- ✅ messages
- ✅ query_analytics

**If you see all 8 tables: Perfect! ✅**

---

## Step 6: Get Your API Keys (1 minute)

### 6.1 Open Settings
- Click **"Settings"** in left sidebar (gear icon at bottom)

### 6.2 Open API Settings
- Click **"API"** in the settings submenu

### 6.3 Copy Project URL
Under **"Project URL"** section:
- You'll see a URL like: `https://xxxxxxxxxxxxx.supabase.co`
- Click the **copy icon** next to it
- **SAVE THIS** - You'll need it as `SUPABASE_URL`

### 6.4 Copy API Keys

**Anon / Public Key:**
- Scroll down to **"Project API keys"**
- Find **"anon"** **"public"**
- Click the **copy icon**
- **SAVE THIS** - You'll need it as `SUPABASE_KEY`

**Service Role Key:**
- In the same section, find **"service_role"**
- Click **"Reveal"** to show the key
- Click the **copy icon** to copy it
- **SAVE THIS** - You'll need it as `SUPABASE_SERVICE_ROLE_KEY`
- ⚠️ **IMPORTANT: Keep this secret! Never commit to git!**

---

## ✅ Setup Complete!

You should now have:
- [x] Supabase project created
- [x] pgvector extension enabled
- [x] 8 database tables created
- [x] 3 API keys saved:
  1. **SUPABASE_URL** (Project URL)
  2. **SUPABASE_KEY** (anon/public key)
  3. **SUPABASE_SERVICE_ROLE_KEY** (service_role key)

---

## What's Next?

Tell me when you have:
1. ✅ All 8 tables showing in Table Editor
2. ✅ Your 3 API keys copied

And I'll help you configure the backend!

---

## Troubleshooting

**Problem: Can't see SQL Editor**
- Make sure your project finished setting up (check for "Setting up project..." message)
- Refresh the page

**Problem: Extension command fails**
- The extension might already be enabled (that's OK!)
- Continue to next step

**Problem: Schema SQL fails**
- Make sure you copied the ENTIRE schema.sql file
- Try running it again (it's safe to re-run)

**Problem: Tables not showing**
- Refresh the Table Editor page
- Click on "Table Editor" in left sidebar again

**Problem: Can't find API keys**
- Settings → API (in left sidebar)
- Scroll down to "Project API keys" section
