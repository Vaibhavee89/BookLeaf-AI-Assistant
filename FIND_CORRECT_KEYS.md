# Finding the Correct Supabase API Keys

## ⚠️ Important: Key Format

The correct Supabase keys should look like this:
- Start with: `eyJ...`
- Very long strings (200+ characters)
- Example: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS...`

## What you're looking for:

### On the API Settings page, scroll down to find:

**Section: "Project API keys"**

You should see TWO keys:

1. **anon / public**
   - Label says: "anon" or "anon public"
   - The key starts with `eyJ...`
   - Usually already visible (not hidden)
   - This is your ANON key

2. **service_role**
   - Label says: "service_role"
   - Click "Reveal" to show it
   - Also starts with `eyJ...`
   - This is your SERVICE_ROLE key

## Screenshot tips:
- Scroll down on the API page
- Look for "Project API keys" heading
- You should see two large text boxes with long keys

---

If you see keys that start with `sb_publishable_`, that's a different type of key and not what we need for this backend.
