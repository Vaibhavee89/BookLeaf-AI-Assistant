#!/bin/bash

echo ""
echo "============================================================"
echo "Testing YOUR Supabase Connection"
echo "============================================================"
echo ""

cd /Users/vaibhavee/project/Bookleaf_Assignment/backend
source venv/bin/activate

echo "1. Testing DNS resolution..."
nslookup frpjbfuslgsirqdjdczy.supabase.co 2>&1 | grep -E "Address:|can't find" | head -3

echo ""
echo "2. Testing HTTP connection..."
curl -s --connect-timeout 5 -I https://frpjbfuslgsirqdjdczy.supabase.co/rest/v1/ 2>&1 | head -2

echo ""
echo "3. Testing Supabase client..."
python3 -c "
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

try:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    result = client.table('authors').select('id').limit(1).execute()
    print('✅ SUCCESS! Supabase is accessible')
    print(f'   Authors table query worked')
except Exception as e:
    print(f'❌ FAILED: {e}')
"

echo ""
echo "============================================================"
echo "If all tests pass, run: python3 backend/scripts/seed_data.py"
echo "============================================================"
echo ""
