#!/bin/bash
# AI Marketing Hub — Full API Test Suite
BASE="http://localhost:8000"
RESULTS="/tmp/test_results.txt"
> "$RESULTS"

test_api() {
    local name="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}\n%{time_total}" "$url" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}\n%{time_total}" -X POST -H "Content-Type: application/json" -d "$data" "$url" 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -1 | head -1)
    time_taken=$(echo "$response" | tail -1)
    http_code=$(echo "$response" | sed -n 'x;$p' | tr -d '[:space:]')
    body=$(echo "$response" | sed '$d' | sed '$d')
    
    # Extract status code and time properly
    lines=$(echo "$response" | wc -l)
    time_taken=$(echo "$response" | tail -1)
    http_code=$(echo "$response" | tail -2 | head -1)
    body=$(echo "$response" | head -n $((lines - 2)))
    
    if [ "$http_code" = "200" ]; then
        echo "✅ $name: $http_code (${time_taken}s)" | tee -a "$RESULTS"
        echo "   Data: $(echo "$body" | head -c 200)" >> "$RESULTS"
    else
        echo "❌ $name: $http_code (${time_taken}s)" | tee -a "$RESULTS"
        echo "   Error: $(echo "$body" | head -c 200)" >> "$RESULTS"
    fi
    echo "" >> "$RESULTS"
}

echo "========================================" | tee -a "$RESULTS"
echo "AI Marketing Hub — API Test Report" | tee -a "$RESULTS"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$RESULTS"
echo "========================================" | tee -a "$RESULTS"
echo "" | tee -a "$RESULTS"

# 1. Health
test_api "Health Check" "GET" "$BASE/health"

# 2. SERP Live (SerpAPI - Google SERP)
test_api "SERP Live (SerpAPI)" "POST" "$BASE/api/serp/live" '{"keyword":"mitsubishi binh phuoc","location":"vn","num_results":5}'

# 3. SEO Audit URL
test_api "SEO Audit URL" "POST" "$BASE/api/audit-url" '{"url":"https://mitsubishibinhphuoc.com.vn/","primary_keyword":"mitsubishi binh phuoc"}'

# 4. Technical SEO Scan
test_api "Technical SEO Scan" "POST" "$BASE/api/tech-seo/scan" '{"url":"https://mitsubishibinhphuoc.com.vn/"}'

# 5. Backlinks Analyze
test_api "Backlinks Analyze" "POST" "$BASE/api/backlinks/analyze" '{"url":"https://mitsubishibinhphuoc.com.vn/"}'

# 6. GEO Analyze
test_api "GEO Analyze" "POST" "$BASE/api/geo/analyze" '{"url":"https://mitsubishibinhphuoc.com.vn/","keyword":"mitsubishi binh phuoc"}'

# 7. Content Polish
test_api "Content Polish" "POST" "$BASE/api/content/polish" '{"raw_content":"Trong boi canh thi truong oto Viet Nam, Mitsubishi Binh Phuoc tu hao la dai ly chinh hang."}'

# 8. Content Spin
test_api "Content Spin" "POST" "$BASE/api/content/spin" '{"content":"Mitsubishi Binh Phuoc la dai ly chinh hang xe Mitsubishi.","level":"medium"}'

# 9. Plan Content
test_api "Plan Content" "POST" "$BASE/api/plan-content" '{"primary_keyword":"xe mitsubishi xpander","target_audience":"khach hang mua oto"}'

# 10. Competitor Gap
test_api "Competitor Gap" "POST" "$BASE/api/competitor-gap" '{"my_url":"https://mitsubishibinhphuoc.com.vn/","competitor_urls":["https://www.mitsubishibinhphuoc.com/"],"primary_keyword":"mitsubishi binh phuoc"}'

# 11. Data Status
test_api "Data Connector Status" "GET" "$BASE/api/data/status"

# 12. Auth Status
test_api "Google Auth Status" "GET" "$BASE/auth/google/status"

# 13. Sites List
test_api "Sites List" "GET" "$BASE/api/sites/list"

# 14. Rank Tracker
test_api "Rank Tracker Keywords" "GET" "$BASE/api/rank-tracker/keywords"

# 15. Calendar Items
test_api "Calendar Items" "GET" "$BASE/api/calendar/items"

# 16. Calendar Stats
test_api "Calendar Stats" "GET" "$BASE/api/calendar/stats"

# 17. A/B Test List
test_api "A/B Test List" "GET" "$BASE/api/ab-test/list"

# 18. Convert Formats
test_api "Convert Formats" "GET" "$BASE/api/convert/formats"

# 19. GEO Generate Schema
test_api "GEO Generate Schema" "POST" "$BASE/api/geo/generate-schema" '{"name":"Mitsubishi Motors Binh Phuoc","address":"1524 Phu Rieng Do","phone":"0924555553","url":"https://mitsubishibinhphuoc.com.vn/"}'

# 20. Report Generate
test_api "Report Generate" "POST" "$BASE/api/report/generate" '{"url":"https://mitsubishibinhphuoc.com.vn/","keyword":"mitsubishi binh phuoc"}'

# 21. SERP Deep Analyze
test_api "SERP Deep Analyze" "POST" "$BASE/api/serp/deep-analyze" '{"keyword":"mitsubishi binh phuoc","urls":["https://mitsubishibinhphuoc.com.vn/"]}'

# 22. GEO FAQ
test_api "GEO Generate FAQ" "POST" "$BASE/api/geo/generate-faq" '{"url":"https://mitsubishibinhphuoc.com.vn/"}'

# 23. Suggest Topics
test_api "Calendar Suggest Topics" "POST" "$BASE/api/calendar/suggest-topics" '{"niche":"oto","count":3}'

# 24. Opportunities
test_api "Opportunity Score" "POST" "$BASE/api/opportunities?url=https://mitsubishibinhphuoc.com.vn/&keyword=mitsubishi+binh+phuoc" '{}'

echo "" | tee -a "$RESULTS"
echo "========================================" | tee -a "$RESULTS"
PASS=$(grep -c "✅" "$RESULTS")
FAIL=$(grep -c "❌" "$RESULTS")
echo "TOTAL: $((PASS + FAIL)) | PASS: $PASS | FAIL: $FAIL" | tee -a "$RESULTS"
echo "========================================" | tee -a "$RESULTS"

cat "$RESULTS"
