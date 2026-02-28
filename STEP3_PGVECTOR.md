# Step 3: Enable pgvector (1 minute)

## 📍 YOU ARE HERE

Your Supabase project is ready! Now we need to enable the vector extension for AI embeddings.

## What to do NOW:

### 1. Find "SQL Editor" in left sidebar
- Look at the LEFT side of your screen
- Find the icon that looks like `</>` or says "SQL Editor"
- **CLICK IT**

### 2. Click "+ New query"
- You'll see this button at the top right
- It might also say "New query"
- **CLICK IT**

### 3. Copy this SQL command:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 4. Paste it into the editor
- Click in the big text area
- Paste the command (Cmd+V on Mac, Ctrl+V on Windows)

### 5. Click "RUN" button
- Look for "Run" button (usually top right)
- Or press Cmd+Enter (Mac) or Ctrl+Enter (Windows)

### 6. Check for success
You should see: ✅ **"Success. No rows returned"** or similar

---

## ✅ When done, tell me: "pgvector enabled"

## 🆘 Issues?

**Can't find SQL Editor?**
- It's in the left sidebar
- Icon looks like code brackets `</>`
- Below "Home" and above "Database"

**Error message?**
- Tell me what it says
- It might say "extension already exists" - that's OK!

**Nothing happens when clicking Run?**
- Make sure you pasted the SQL command
- Try clicking in the text editor first
