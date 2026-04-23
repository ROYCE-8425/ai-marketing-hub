"""
AI Keyword Analyzer — Multi-provider (Z.AI → Gemini → built-in heuristic)

Fetches real GSC keywords and uses AI to:
1. Analyze current keyword performance
2. Suggest new keyword opportunities
3. Group keywords by topic clusters
4. Recommend content strategy
"""

import os
import httpx
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# ── AI Provider URLs ─────────────────────────────────────────────────────────
ZAI_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def _get_gsc_keywords(days: int = 30, limit: int = 200) -> List[Dict[str, Any]]:
    """Fetch all keywords from Google Search Console."""
    client_id = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
    secret = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET", "")
    refresh = os.getenv("GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN", "")
    site_url = os.getenv("GSC_SITE_URL", "")

    if not all([client_id, secret, refresh, site_url]):
        return []

    try:
        # Get access token
        token_resp = httpx.post("https://oauth2.googleapis.com/token", data={
            "client_id": client_id,
            "client_secret": secret,
            "refresh_token": refresh,
            "grant_type": "refresh_token",
        }, timeout=10.0)
        access_token = token_resp.json().get("access_token", "")
        if not access_token:
            return []

        # Query GSC
        import urllib.parse
        encoded_site = urllib.parse.quote(site_url, safe="")
        api_url = f"https://www.googleapis.com/webmasters/v3/sites/{encoded_site}/searchAnalytics/query"

        end_date = datetime.now().date() - timedelta(days=3)
        start_date = end_date - timedelta(days=days)

        resp = httpx.post(api_url, headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }, json={
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "dimensions": ["query"],
            "rowLimit": limit,
        }, timeout=15.0)

        if resp.status_code != 200:
            return []

        rows = resp.json().get("rows", [])
        return [
            {
                "keyword": row["keys"][0],
                "clicks": int(row["clicks"]),
                "impressions": int(row["impressions"]),
                "ctr": round(row["ctr"], 4),
                "position": round(row["position"], 1),
            }
            for row in rows
        ]
    except Exception:
        return []


# ── AI Providers ─────────────────────────────────────────────────────────────

def _call_groq(prompt: str, system_prompt: str) -> str:
    """Call Groq (fastest, free tier)."""
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY not configured")

    resp = httpx.post("https://api.groq.com/openai/v1/chat/completions", headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }, json={
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
    }, timeout=30.0)

    if resp.status_code != 200:
        raise ValueError(f"Groq error {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"]


def _call_zai(prompt: str, system_prompt: str) -> str:
    """Call Z.AI (Zhipu GLM)."""
    api_key = os.getenv("ZAI_API_KEY", "")
    if not api_key:
        raise ValueError("ZAI_API_KEY not configured")

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]

    resp = httpx.post(ZAI_API_URL, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }, json={
        "model": "glm-4-flash",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4096,
    }, timeout=30.0)

    if resp.status_code != 200:
        raise ValueError(f"Z.AI error {resp.status_code}")
    return resp.json()["choices"][0]["message"]["content"]


def _call_gemini(prompt: str, system_prompt: str) -> str:
    """Call Google Gemini (free tier)."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not configured")

    url = f"{GEMINI_API_URL}?key={api_key}"
    resp = httpx.post(url, headers={"Content-Type": "application/json"}, json={
        "contents": [
            {"role": "user", "parts": [{"text": f"{system_prompt}\n\n{prompt}"}]},
        ],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096},
    }, timeout=60.0)

    if resp.status_code != 200:
        raise ValueError(f"Gemini error {resp.status_code}: {resp.text[:200]}")
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


def _call_openai_compatible(prompt: str, system_prompt: str) -> str:
    """Call any OpenAI-compatible API (configurable via env)."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not configured")

    resp = httpx.post(f"{base_url}/chat/completions", headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }, json={
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
    }, timeout=60.0)

    if resp.status_code != 200:
        raise ValueError(f"OpenAI error {resp.status_code}")
    return resp.json()["choices"][0]["message"]["content"]


def _call_ai(prompt: str, system_prompt: str) -> str:
    """Try multiple AI providers in order: Groq → Gemini → Z.AI → OpenAI-compat."""
    errors = []

    # Try Groq first (fastest, works from VN)
    if os.getenv("GROQ_API_KEY"):
        try:
            return _call_groq(prompt, system_prompt)
        except Exception as e:
            errors.append(f"Groq: {e}")

    # Try Gemini
    if os.getenv("GEMINI_API_KEY"):
        try:
            return _call_gemini(prompt, system_prompt)
        except Exception as e:
            errors.append(f"Gemini: {e}")

    # Try Z.AI
    if os.getenv("ZAI_API_KEY"):
        try:
            return _call_zai(prompt, system_prompt)
        except Exception as e:
            errors.append(f"Z.AI: {e}")

    # Try OpenAI-compatible
    if os.getenv("OPENAI_API_KEY"):
        try:
            return _call_openai_compatible(prompt, system_prompt)
        except Exception as e:
            errors.append(f"OpenAI: {e}")

    raise ValueError(f"All AI providers failed: {'; '.join(errors) or 'No API keys configured'}")


# ── Built-in keyword analysis (no AI needed) ────────────────────────────────

def _builtin_keyword_analysis(gsc_keywords: List[Dict], target_keyword: str) -> Dict[str, Any]:
    """Heuristic-based keyword analysis when no AI API is available."""
    if not gsc_keywords:
        return {
            "summary": "Chưa có dữ liệu GSC. Cần kết nối Google Search Console để phân tích.",
            "recommended_keywords": [],
            "keyword_clusters": [],
            "content_strategy": [],
            "top_performing": [],
            "quick_wins": [],
        }

    sorted_by_imp = sorted(gsc_keywords, key=lambda x: x["impressions"], reverse=True)
    sorted_by_clicks = sorted(gsc_keywords, key=lambda x: x["clicks"], reverse=True)

    # Top performing
    top_performing = [
        {"keyword": kw["keyword"], "reason": f"Vị trí {kw['position']}, {kw['clicks']} clicks, {kw['impressions']} hiển thị"}
        for kw in sorted_by_clicks[:5] if kw["clicks"] > 0
    ]

    # Quick wins: position 8-20, has impressions
    quick_wins = [
        {
            "keyword": kw["keyword"],
            "current_position": kw["position"],
            "action": f"Cải thiện từ vị trí {kw['position']} lên top 5 — đang có {kw['impressions']} lượt hiển thị/tháng"
        }
        for kw in sorted_by_imp if 8 <= kw["position"] <= 25 and kw["impressions"] >= 3
    ][:10]

    # Group keywords by common words
    clusters = {}
    for kw in gsc_keywords:
        words = kw["keyword"].lower().split()
        for w in words:
            if len(w) > 3 and w not in ("https", "http", "www", "com", "html"):
                if w not in clusters:
                    clusters[w] = []
                clusters[w].append(kw["keyword"])

    keyword_clusters = [
        {"cluster_name": word.capitalize(), "keywords": list(set(kws))[:8], "suggested_content": f"Viết bài tổng hợp về {word}"}
        for word, kws in sorted(clusters.items(), key=lambda x: -len(x[1]))[:6]
        if len(kws) >= 2
    ]

    total_clicks = sum(kw["clicks"] for kw in gsc_keywords)
    total_imp = sum(kw["impressions"] for kw in gsc_keywords)
    avg_ctr = round(total_clicks / max(total_imp, 1) * 100, 1)

    summary = (
        f"Website có {len(gsc_keywords)} từ khóa trên Google trong 30 ngày qua. "
        f"Tổng: {total_clicks} clicks, {total_imp} hiển thị, CTR trung bình {avg_ctr}%. "
        f"Có {len(quick_wins)} từ khóa 'quick win' (vị trí 8-25) có thể cải thiện nhanh."
    )

    return {
        "summary": summary,
        "top_performing": top_performing,
        "recommended_keywords": [],
        "keyword_clusters": keyword_clusters,
        "content_strategy": [],
        "quick_wins": quick_wins,
    }


# ── Main function ────────────────────────────────────────────────────────────

def analyze_keywords_with_ai(target_keyword: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function: Fetch GSC keywords → AI analysis → keyword recommendations.
    """
    result = {
        "analyzed_at": datetime.now().isoformat(),
        "site_url": os.getenv("GSC_SITE_URL", ""),
        "gsc_keywords": [],
        "total_clicks": 0,
        "total_impressions": 0,
        "ai_analysis": "",
        "recommended_keywords": [],
        "keyword_clusters": [],
        "content_strategy": [],
        "top_performing": [],
        "quick_wins": [],
        "summary": "",
        "data_source": "mock",
        "ai_provider": "none",
    }

    # Step 1: Fetch GSC keywords
    gsc_keywords = _get_gsc_keywords(days=30, limit=200)

    if gsc_keywords:
        result["gsc_keywords"] = gsc_keywords
        result["total_clicks"] = sum(kw["clicks"] for kw in gsc_keywords)
        result["total_impressions"] = sum(kw["impressions"] for kw in gsc_keywords)
        result["data_source"] = "live_gsc"

    # Step 2: Build AI prompt
    system_prompt = """Bạn là chuyên gia SEO hàng đầu Việt Nam. Nhiệm vụ:
1. Phân tích dữ liệu từ khóa từ Google Search Console
2. Đề xuất từ khóa mới có tiềm năng
3. Phân nhóm từ khóa theo chủ đề (topic clusters)
4. Đưa ra chiến lược nội dung cụ thể

Trả lời HOÀN TOÀN bằng tiếng Việt.
Trả về kết quả dưới dạng JSON (chỉ JSON, không có text khác):
{
  "summary": "Tóm tắt ngắn gọn",
  "top_performing": [{"keyword": "...", "reason": "..."}],
  "recommended_keywords": [
    {"keyword": "...", "search_intent": "informational|commercial|transactional", "difficulty": "easy|medium|hard", "priority": "high|medium|low", "reason": "..."}
  ],
  "keyword_clusters": [
    {"cluster_name": "...", "keywords": ["..."], "suggested_content": "..."}
  ],
  "content_strategy": [
    {"title": "...", "target_keyword": "...", "content_type": "blog|landing|product|guide", "priority": "high|medium|low", "description": "..."}
  ],
  "quick_wins": [{"keyword": "...", "current_position": 0, "action": "..."}]
}"""

    if gsc_keywords:
        sorted_kw = sorted(gsc_keywords, key=lambda x: x["impressions"], reverse=True)
        top_20 = sorted_kw[:20]

        kw_table = "\n".join([
            f"- {kw['keyword']}: clicks={kw['clicks']}, imp={kw['impressions']}, ctr={kw['ctr']}, pos={kw['position']}"
            for kw in top_20
        ])

        target_info = f"\nTừ khóa mục tiêu: {target_keyword}" if target_keyword else ""
        site = os.getenv("GSC_SITE_URL", "")

        prompt = f"""Website: {site}{target_info}

Dữ liệu GSC 30 ngày: {result['total_clicks']} clicks, {result['total_impressions']} impressions, {len(gsc_keywords)} từ khóa

Top 20 từ khóa:
{kw_table}

Tất cả từ khóa: {json.dumps([kw['keyword'] for kw in gsc_keywords], ensure_ascii=False)}

Phân tích và đề xuất 10-15 từ khóa MỚI + topic clusters + chiến lược nội dung + quick wins."""
    else:
        prompt = f"""Website: {os.getenv('GSC_SITE_URL', '')}
Ngành: đại lý xe Mitsubishi Bình Phước
Từ khóa mục tiêu: {target_keyword or 'mitsubishi bình phước'}

Đề xuất 15-20 từ khóa tiềm năng + topic clusters + chiến lược nội dung."""

    # Step 3: Try AI, fallback to built-in
    try:
        ai_response = _call_ai(prompt, system_prompt)
        result["ai_analysis"] = ai_response
        result["ai_provider"] = "ai"

        # Parse JSON from response
        # Try to find JSON block (may be wrapped in ```json ... ```)
        clean = ai_response.strip()
        # Remove markdown code fences
        clean = re.sub(r'^```json?\s*', '', clean, flags=re.MULTILINE)
        clean = re.sub(r'```\s*$', '', clean, flags=re.MULTILINE)

        json_start = clean.find("{")
        json_end = clean.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            parsed = json.loads(clean[json_start:json_end])
            result["recommended_keywords"] = parsed.get("recommended_keywords", [])
            result["keyword_clusters"] = parsed.get("keyword_clusters", [])
            result["content_strategy"] = parsed.get("content_strategy", [])
            result["summary"] = parsed.get("summary", "")
            result["top_performing"] = parsed.get("top_performing", [])
            result["quick_wins"] = parsed.get("quick_wins", [])
    except Exception as e:
        # Fallback to built-in analysis
        result["ai_error"] = str(e)
        result["ai_provider"] = "builtin"
        builtin = _builtin_keyword_analysis(gsc_keywords, target_keyword or "")
        result.update(builtin)

    return result
