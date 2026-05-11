"""
Google Custom Search JSON API Client

Calls the official Google Custom Search API (customsearch.googleapis.com)
to retrieve search results from a Programmable Search Engine.

Requirements:
  - GOOGLE_CUSTOM_SEARCH_API_KEY (API key from Google Cloud Console)
  - GOOGLE_CUSTOM_SEARCH_ENGINE_ID (Search Engine ID / cx)

Limitations vs DataForSEO:
  - Results come from Programmable Search Engine, not identical to organic Google
  - No SEO metrics (search volume, CPC, competition)
  - Free tier: 100 queries/day
  - Max 10 results per request (pagination possible but consumes quota)

This module is designed as a fallback when DataForSEO is not configured.
"""

import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx


# Google Custom Search API endpoint
_CSE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"

# Location code → Google gl param (geolocation)
_GL_MAP = {
    "vn": "vn",
    "us": "us",
    "uk": "uk",
    "au": "au",
    "in": "in",
    "sg": "sg",
    "jp": "jp",
}

# Location code → Google lr param (language restrict)
_LR_MAP = {
    "vn": "lang_vi",
    "us": "lang_en",
    "uk": "lang_en",
    "au": "lang_en",
    "in": "lang_en",
    "sg": "lang_en",
    "jp": "lang_ja",
}


def _get_credentials() -> tuple[Optional[str], Optional[str]]:
    """Return (api_key, cx) or (None, None) if not configured."""
    api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
    return api_key, cx


# ── Daily quota limiter (stay within free tier: 100/day) ──────────────────────
# Configurable via .env: CSE_DAILY_LIMIT=30 (default)

def _get_daily_limit() -> int:
    """Get daily quota limit from env or default to 30."""
    return int(os.getenv("CSE_DAILY_LIMIT", "30"))

def _check_and_increment_quota() -> bool:
    """
    Check if we're within daily quota. Returns True if OK to proceed.
    Uses a simple file-based counter that resets each day.
    """
    from datetime import date
    quota_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache")
    os.makedirs(quota_dir, exist_ok=True)
    quota_file = os.path.join(quota_dir, "cse_quota.json")

    today = date.today().isoformat()
    data = {"date": today, "count": 0}

    # Read existing counter
    try:
        if os.path.exists(quota_file):
            import json
            with open(quota_file, "r") as f:
                data = json.load(f)
            if data.get("date") != today:
                data = {"date": today, "count": 0}
    except Exception:
        data = {"date": today, "count": 0}

    if data["count"] >= _get_daily_limit():
        return False

    # Increment and save
    data["count"] += 1
    try:
        import json
        with open(quota_file, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

    return True


def search_google_cse(
    keyword: str,
    location: str = "vn",
    num_results: int = 10,
) -> Optional[Dict[str, Any]]:
    """
    Search using Google Custom Search JSON API.

    Returns:
      - Dict with organic_results, source="google_custom_search" on success
      - None if credentials are not configured
      - Dict with source="api_error" on API failure
      - Dict with source="quota_exceeded" if daily limit reached

    Note: Google CSE returns max 10 results per request.
    For num_results > 10, we make a second request (costs extra quota).
    Daily limit: 90 queries (free tier = 100, we keep 10 as safety margin).
    """
    api_key, cx = _get_credentials()
    if not api_key or not cx:
        return None

    # Check daily quota BEFORE making API call
    if not _check_and_increment_quota():
        return {
            "keyword": keyword,
            "organic_results": [],
            "serp_features": [],
            "total_results": 0,
            "results_count": 0,
            "source": "quota_exceeded",
            "error": f"Đã đạt giới hạn {_get_daily_limit()} queries/ngày (free tier). Thử lại ngày mai hoặc dùng DataForSEO.",
        }

    # Google CSE max 10 per request
    first_batch = min(num_results, 10)

    try:
        results = _fetch_cse(api_key, cx, keyword, location, start=1, num=first_batch)

        # If user wants > 10 and first batch returned 10, fetch more
        if num_results > 10 and len(results.get("organic_results", [])) >= 10:
            extra = _fetch_cse(api_key, cx, keyword, location, start=11, num=min(num_results - 10, 10))
            results["organic_results"].extend(extra.get("organic_results", []))
            results["results_count"] = len(results["organic_results"])

        return results

    except httpx.HTTPStatusError as exc:
        error_msg = _format_google_cse_error(exc)
        return {
            "keyword": keyword,
            "organic_results": [],
            "serp_features": [],
            "total_results": 0,
            "results_count": 0,
            "source": "api_error",
            "error": error_msg,
        }
    except Exception as exc:
        return {
            "keyword": keyword,
            "organic_results": [],
            "serp_features": [],
            "total_results": 0,
            "results_count": 0,
            "source": "api_error",
            "error": f"Google Custom Search lỗi: {str(exc)[:200]}",
        }


def _format_google_cse_error(exc: httpx.HTTPStatusError) -> str:
    """Return Vietnamese, actionable Google Custom Search error message."""
    status_code = exc.response.status_code
    detail = ""
    try:
        body = exc.response.json()
        detail = body.get("error", {}).get("message", "")
    except Exception:
        detail = exc.response.text[:200]

    if status_code == 403 and "access to Custom Search JSON API" in detail:
        return (
            "Google Custom Search API chưa được bật cho project này. "
            "Vào Google Cloud Console → APIs & Services → Library → bật Custom Search JSON API, "
            "sau đó kiểm tra API key và Search Engine ID."
        )
    if status_code == 403 and ("quota" in detail.lower() or "limit" in detail.lower()):
        return "Google Custom Search đã hết quota/ngày. Thử lại ngày mai hoặc cấu hình DataForSEO."
    if status_code == 400 and "cx" in detail.lower():
        return "Search Engine ID (cx) không hợp lệ. Kiểm tra GOOGLE_CUSTOM_SEARCH_ENGINE_ID trong backend/.env."
    if status_code in (401, 403):
        return f"Google Custom Search API bị từ chối quyền truy cập ({status_code}). Kiểm tra API key và quyền API."
    return f"Google Custom Search API HTTP {status_code}: {detail[:200]}" if detail else f"Google Custom Search API HTTP {status_code}"


def _fetch_cse(
    api_key: str,
    cx: str,
    keyword: str,
    location: str,
    start: int = 1,
    num: int = 10,
) -> Dict[str, Any]:
    """Make a single request to Google Custom Search API and normalize results."""
    params = {
        "key": api_key,
        "cx": cx,
        "q": keyword,
        "num": num,
        "start": start,
        "gl": _GL_MAP.get(location.lower(), "us"),
        "lr": _LR_MAP.get(location.lower(), "lang_en"),
    }

    with httpx.Client(timeout=15.0) as client:
        resp = client.get(_CSE_ENDPOINT, params=params)
        resp.raise_for_status()
        data = resp.json()

    # Parse search information
    search_info = data.get("searchInformation", {})
    total_results_str = search_info.get("totalResults", "0")
    try:
        total_results = int(total_results_str)
    except (ValueError, TypeError):
        total_results = 0

    # Parse items → organic_results
    organic_results = []
    items = data.get("items", [])
    for i, item in enumerate(items, start=start):
        url = item.get("link", "")
        title = item.get("title", "")
        if not url:
            continue

        try:
            domain = urlparse(url).netloc.replace("www.", "")
        except Exception:
            domain = ""

        organic_results.append({
            "position": i,
            "title": title,
            "url": url,
            "domain": domain,
            "snippet": item.get("snippet", ""),
            "breadcrumb": item.get("formattedUrl", ""),
        })

    return {
        "keyword": keyword,
        "organic_results": organic_results,
        "serp_features": [],  # CSE doesn't provide SERP features
        "total_results": total_results,
        "results_count": len(organic_results),
        "source": "google_custom_search",
        # No SEO metrics from CSE
        "search_volume": None,
        "cpc": None,
        "competition": None,
    }
