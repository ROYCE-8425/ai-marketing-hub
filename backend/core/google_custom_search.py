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

    Note: Google CSE returns max 10 results per request.
    For num_results > 10, we make a second request (costs extra quota).
    """
    api_key, cx = _get_credentials()
    if not api_key or not cx:
        return None

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
        error_msg = f"Google Custom Search API HTTP {exc.response.status_code}"
        try:
            body = exc.response.json()
            error_detail = body.get("error", {}).get("message", "")
            if error_detail:
                error_msg += f": {error_detail[:200]}"
        except Exception:
            pass
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
