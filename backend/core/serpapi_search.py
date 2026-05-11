"""
SerpAPI Client — Real Google SERP Results

Uses SerpAPI (serpapi.com) to fetch actual Google Search results.
This provides real Google rankings for SEO analysis.

Requirements:
  - SERPAPI_KEY (from https://serpapi.com/manage-api-key)

Free tier: 100 searches/month.
"""

import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx


# SerpAPI endpoint
_SERPAPI_ENDPOINT = "https://serpapi.com/search.json"

# Location → Google gl param
_GL_MAP = {
    "vn": "vn",
    "us": "us",
    "uk": "uk",
    "au": "au",
    "in": "in",
    "sg": "sg",
    "jp": "jp",
}

# Location → Google hl param (interface language)
_HL_MAP = {
    "vn": "vi",
    "us": "en",
    "uk": "en",
    "au": "en",
    "in": "en",
    "sg": "en",
    "jp": "ja",
}


def _get_serpapi_key() -> Optional[str]:
    """Return SerpAPI key or None."""
    return os.getenv("SERPAPI_KEY")


def search_serpapi(
    keyword: str,
    location: str = "vn",
    num_results: int = 10,
) -> Optional[Dict[str, Any]]:
    """
    Search Google via SerpAPI.

    Returns:
      - Dict with organic_results, source="serpapi_google" on success
      - None if API key is not configured
      - Dict with source="api_error" on failure
    """
    api_key = _get_serpapi_key()
    if not api_key:
        return None

    gl = _GL_MAP.get(location.lower(), "us")
    hl = _HL_MAP.get(location.lower(), "en")
    num = max(5, min(20, num_results))

    params = {
        "engine": "google",
        "q": keyword,
        "gl": gl,
        "hl": hl,
        "num": num,
        "api_key": api_key,
    }

    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.get(_SERPAPI_ENDPOINT, params=params)
            resp.raise_for_status()
            data = resp.json()

        return _format_serpapi_results(data, keyword)

    except httpx.HTTPStatusError as exc:
        error_msg = _format_serpapi_error(exc)
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
            "error": f"SerpAPI lỗi: {str(exc)[:200]}",
        }


def _format_serpapi_results(data: dict, keyword: str) -> Dict[str, Any]:
    """Convert SerpAPI response to our standard SERP format."""
    organic_raw = data.get("organic_results", [])
    search_info = data.get("search_information", {})
    total_results = search_info.get("total_results", 0)

    organic_results = []
    for item in organic_raw:
        url = item.get("link", "")
        title = item.get("title", "")
        if not url:
            continue

        try:
            domain = urlparse(url).netloc.replace("www.", "")
        except Exception:
            domain = ""

        organic_results.append({
            "position": item.get("position", len(organic_results) + 1),
            "title": title,
            "url": url,
            "domain": domain,
            "snippet": item.get("snippet", ""),
            "breadcrumb": item.get("displayed_link", ""),
        })

    # Extract SERP features
    serp_features = []
    if data.get("answer_box"):
        serp_features.append("featured_snippet")
    if data.get("knowledge_graph"):
        serp_features.append("knowledge_panel")
    if data.get("local_results"):
        serp_features.append("local_pack")
    if data.get("related_questions"):
        serp_features.append("people_also_ask")
    if data.get("top_stories"):
        serp_features.append("top_stories")
    if data.get("shopping_results"):
        serp_features.append("shopping")
    if data.get("images_results"):
        serp_features.append("images")
    if data.get("inline_videos"):
        serp_features.append("videos")

    return {
        "keyword": keyword,
        "organic_results": organic_results,
        "serp_features": serp_features,
        "total_results": total_results or len(organic_results),
        "results_count": len(organic_results),
        "source": "serpapi_google",
        "search_volume": None,
        "cpc": None,
        "competition": None,
    }


def _format_serpapi_error(exc: httpx.HTTPStatusError) -> str:
    """Return Vietnamese, actionable SerpAPI error message."""
    status_code = exc.response.status_code
    detail = ""
    try:
        body = exc.response.json()
        detail = body.get("error", "")
    except Exception:
        detail = exc.response.text[:200]

    if status_code == 401:
        return "SerpAPI key không hợp lệ. Kiểm tra SERPAPI_KEY trong backend/.env."
    if status_code == 429:
        return "SerpAPI đã hết quota tháng này (100 searches/tháng free). Nâng cấp hoặc chờ tháng sau."
    return f"SerpAPI HTTP {status_code}: {detail[:200]}" if detail else f"SerpAPI HTTP {status_code}"
