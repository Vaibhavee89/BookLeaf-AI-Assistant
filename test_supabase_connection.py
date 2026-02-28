"""Test Supabase connection."""

import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print(f"\n{'='*60}")
print("Supabase Connection Test")
print(f"{'='*60}\n")

print(f"Testing URL: {SUPABASE_URL}")
print(f"Key configured: {'Yes' if SUPABASE_KEY else 'No'}\n")

# Test 1: DNS Resolution
print("Test 1: DNS Resolution")
print("-" * 60)
import socket
try:
    domain = SUPABASE_URL.replace('https://', '').replace('http://', '').split('/')[0]
    ip = socket.gethostbyname(domain)
    print(f"✅ DNS resolved: {domain} -> {ip}")
except socket.gaierror as e:
    print(f"❌ DNS resolution failed: {e}")
    print("   Domain does not exist in DNS (NXDOMAIN)")

# Test 2: HTTP Connection
print("\nTest 2: HTTP Connection")
print("-" * 60)
try:
    import requests
    response = requests.get(f"{SUPABASE_URL}/rest/v1/", timeout=5)
    print(f"✅ HTTP connection successful: {response.status_code}")
except requests.exceptions.Timeout:
    print("❌ Connection timeout")
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Supabase Client
print("\nTest 3: Supabase Client Connection")
print("-" * 60)
try:
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Try to query a table
    result = client.table("authors").select("id").limit(1).execute()

    if result.data is not None:
        print(f"✅ Supabase client connected successfully!")
        print(f"   Query successful: {len(result.data)} rows returned")
    else:
        print(f"❌ Query returned no data")

except Exception as e:
    print(f"❌ Supabase client connection failed: {e}")

print(f"\n{'='*60}")
print("Test Complete")
print(f"{'='*60}\n")
