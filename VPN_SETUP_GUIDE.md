# VPN Setup for Supabase Access from India

## Problem
Your VPN routes **browser traffic** but not **terminal/command-line traffic**, so:
- ✅ Supabase dashboard loads in browser
- ❌ Terminal commands (Python, curl) still blocked

## Solution: System-Wide VPN Configuration

### Option A: Free VPN Recommendations

#### 1. ProtonVPN (FREE - Best for Development)

**Why ProtonVPN:**
- ✅ Free tier with unlimited data
- ✅ System-wide routing (all apps)
- ✅ macOS native client
- ✅ No bandwidth limits

**Setup Steps:**
1. Download: https://protonvpn.com/download
2. Install macOS app
3. Create free account
4. Connect to any server (US, EU, Japan)
5. **Verify system-wide routing:**
   ```bash
   curl -s https://ipinfo.io/country
   # Should NOT show "IN"
   ```

#### 2. Windscribe (FREE 10GB/month)

1. Download: https://windscribe.com/download
2. Install macOS app
3. Create account (get 10GB free)
4. Connect to US/EU server

#### 3. Cloudflare WARP (FREE - Unlimited)

**Best for development work!**

```bash
# Install via Homebrew
brew install --cask cloudflare-warp

# Or download from: https://1.1.1.1/
```

**Setup:**
1. Install Cloudflare WARP
2. Open app from Applications
3. Click "Connect"
4. It routes ALL traffic (including terminal)

**Verify:**
```bash
curl -s https://ipinfo.io/json
# Should show non-India country
```

### Option B: Configure Existing VPN for Terminal

If you have a VPN app but it's not routing terminal traffic:

#### For macOS Built-in VPN:

1. **System Settings → Network**
2. Click your VPN connection
3. Click **"Advanced..."**
4. Check: **"Send all traffic over VPN connection"**
5. Click **OK** and **Apply**
6. Reconnect VPN

#### For Third-Party VPN Apps:

Most VPN apps have settings like:
- ✅ Enable: "System-wide protection"
- ✅ Enable: "Route all traffic through VPN"
- ✅ Enable: "Kill switch"
- ❌ Disable: "Split tunneling" (this bypasses terminal traffic)

**Example - NordVPN:**
1. Open NordVPN app
2. Settings → Advanced
3. Disable "Split Tunneling"
4. Enable "Kill Switch"
5. Reconnect

**Example - ExpressVPN:**
1. Open ExpressVPN
2. Options → Advanced
3. Enable "Network Lock"
4. Disable "Split Tunneling"
5. Reconnect

### Option C: Alternative DNS (If VPN Fails)

Supabase mentioned "alternative DNS provider". Try:

```bash
# Test with different DNS servers
# Google DNS
nslookup frpjbfuslgsirqdjdczy.supabase.co 8.8.8.8

# Cloudflare DNS
nslookup frpjbfuslgsirqdjdczy.supabase.co 1.1.1.1

# Quad9 DNS
nslookup frpjbfuslgsirqdjdczy.supabase.co 9.9.9.9
```

**If any DNS works**, configure your system to use it:

**macOS:**
1. System Settings → Network
2. Select your network (Wi-Fi or Ethernet)
3. Click "Details..."
4. Go to "DNS" tab
5. Click "+" and add:
   - `8.8.8.8` (Google)
   - `8.8.4.4` (Google)
   - `1.1.1.1` (Cloudflare)
   - `1.0.0.1` (Cloudflare)
6. Click OK and Apply

## Verification Checklist

After setting up VPN, verify it works:

### ✅ Step 1: Check IP Location
```bash
curl -s https://ipinfo.io/json | python3 -m json.tool
```
**Expected**: Country should NOT be "IN" (India)

### ✅ Step 2: Test DNS Resolution
```bash
nslookup frpjbfuslgsirqdjdczy.supabase.co
```
**Expected**: Should return an IP address, NOT "NXDOMAIN"

### ✅ Step 3: Test HTTP Connection
```bash
curl -I https://frpjbfuslgsirqdjdczy.supabase.co/rest/v1/
```
**Expected**: HTTP response headers, NOT timeout

### ✅ Step 4: Test Supabase Client
```bash
cd /Users/vaibhavee/project/Bookleaf_Assignment/backend
source venv/bin/activate
python3 -c "
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
result = client.table('authors').select('id').limit(1).execute()
print('✅ SUCCESS! Supabase accessible via VPN')
"
```
**Expected**: "✅ SUCCESS! Supabase accessible via VPN"

## Recommended Solution

**For Development Work**: Use **Cloudflare WARP**
- Free and unlimited
- System-wide routing
- Easy to toggle on/off
- Doesn't slow down much
- Made by Cloudflare (optimized for developers)

```bash
# Install
brew install --cask cloudflare-warp

# Or download: https://1.1.1.1/
```

## Once VPN Works

Run this to seed Supabase:

```bash
cd /Users/vaibhavee/project/Bookleaf_Assignment

# Verify connection
bash test_your_supabase.sh

# If tests pass, seed database
cd backend && source venv/bin/activate
python3 scripts/seed_data.py
```

## Troubleshooting

### VPN Connected But Terminal Still Fails

**Issue**: Split tunneling or DNS leaks

**Fix**:
```bash
# Flush DNS cache
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# Test again
curl -s https://ipinfo.io/country
```

### VPN Slows Down Everything

**Try**: Cloudflare WARP in "WARP+" mode
- Faster than traditional VPN
- Uses Cloudflare's Argo network

### All VPNs Fail

**Last Resort**: Create new Supabase project in **US East** region
- Some regions work better from India
- See: CREATE_NEW_SUPABASE.md

## Current Status

Your `.env` is configured for:
- Direct Supabase connection (needs VPN)
- Cloudflare Worker proxy (also needs origin DNS to work)

Once VPN routes terminal traffic:
1. Both will work
2. You can seed Supabase
3. Full features unlocked

---

**Next Step**: Install Cloudflare WARP or configure your existing VPN to route all traffic.
