#!/bin/bash
# ===================================================================
# Quick Test Script — Chạy ngoài sandbox (terminal thật)
# ===================================================================
# Cách dùng:
#   cd ai_marketing_hub/backend
#   source venv/bin/activate
#   bash test_quick.sh
# ===================================================================

echo "============================================================"
echo "TEST 1: Google Custom Search API"
echo "============================================================"
python3 -c "
import os; from dotenv import load_dotenv; load_dotenv('.env', override=True)
from core.google_custom_search import search_google_cse
r = search_google_cse('mitsubishi binh phuoc', location='vn', num_results=5)
if r is None: print('❌ Credentials missing')
elif r.get('source') == 'api_error': print(f'❌ {r[\"error\"]}')
else:
    print(f'✅ Source: {r[\"source\"]} | Results: {r[\"results_count\"]}')
    for x in r.get('organic_results', [])[:5]:
        print(f'  #{x[\"position\"]}: {x[\"title\"][:70]}')
        print(f'     → {x[\"url\"][:80]}')
"

echo ""
echo "============================================================"
echo "TEST 2: GA4 Overview"
echo "============================================================"
python3 -c "
import asyncio, os; from dotenv import load_dotenv; load_dotenv('.env', override=True)
from core.ga4_fetcher import get_ga4_overview
g = asyncio.run(get_ga4_overview(7))
print(f'Data source: {g[\"data_source\"]}')
if g.get('error'): print(f'Error: {g[\"error\"][:150]}')
else:
    o = g.get('overview', {})
    print(f'Sessions: {o.get(\"sessions\",0)} | Users: {o.get(\"active_users\",0)} | PV: {o.get(\"pageviews\",0)}')
"

echo ""
echo "============================================================"
echo "TEST 3: OAuth2 Auth URL"
echo "============================================================"
python3 -c "
import asyncio, os; from dotenv import load_dotenv; load_dotenv('.env', override=True)
from routers.api_auth import google_auth_setup
r = asyncio.run(google_auth_setup())
if 'auth_url' in r: print('✅ Auth URL generated OK')
else: print(f'❌ {r.get(\"error\", \"unknown\")}')
"

echo ""
echo "DONE ✅"
