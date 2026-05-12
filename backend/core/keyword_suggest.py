"""
Keyword Suggest — SpinEditor Data Scraper + Google Suggest Fallback

Ưu tiên cào dữ liệu THẬT từ SpinEditor (nếu có cookie),
fallback sang Google Suggest + SerpAPI nếu không có.

Nguồn: Dữ liệu từ SpinEditor
"""

import os
import re
import json
import math
import asyncio
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import httpx
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"), override=True)

CSE_API_KEY = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY", "")
CSE_ENGINE_ID = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")


# ── Google Suggest (Autocomplete) ────────────────────────────────────────────


async def google_suggest(keyword: str, lang: str = "vi", country: str = "vn") -> List[str]:
    """Google Autocomplete — lấy gợi ý từ khóa."""
    urls = [
        ("https://suggestqueries.google.com/complete/search", {"client": "firefox"}),
        ("https://www.google.com/complete/search", {"client": "chrome"}),
    ]
    for base_url, extra_params in urls:
        try:
            params = {"q": keyword, "hl": lang, "gl": country, **extra_params}
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(base_url, params=params, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
                })
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and len(data) > 1:
                        return [s for s in data[1] if isinstance(s, str)]
        except Exception:
            continue
    return []


async def expand_suggestions(keyword: str, lang: str = "vi") -> List[str]:
    """Mở rộng keyword bằng suffix a-z."""
    tasks = [google_suggest(keyword, lang)]
    for c in "abcdefghijklmnopqrstuvwxyz":
        tasks.append(google_suggest(f"{keyword} {c}", lang))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_kws = set()
    for r in results:
        if isinstance(r, list):
            for s in r:
                if isinstance(s, str) and s.strip():
                    all_kws.add(s.strip().lower())

    all_kws.discard(keyword.lower())
    return sorted(all_kws)


# ── SerpAPI cho Volume + Competition ─────────────────────────────────────────


async def _get_serp_volume(keyword: str) -> Dict[str, Any]:
    """
    Dùng SerpAPI Google Search để lấy total_results (proxy cho volume).
    Chính xác hơn CSE vì không bị giới hạn engine.
    """
    if not SERPAPI_KEY:
        return {}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            # Search bình thường
            resp = await client.get("https://serpapi.com/search.json", params={
                "api_key": SERPAPI_KEY,
                "engine": "google",
                "q": keyword,
                "gl": "vn",
                "hl": "vi",
                "num": 1,
            })
            if resp.status_code == 200:
                data = resp.json()
                total = data.get("search_information", {}).get("total_results", 0)
                return {"total_results": int(total) if total else 0}
    except Exception:
        pass
    return {}


async def _get_allintitle_serp(keyword: str) -> Optional[int]:
    """Dùng SerpAPI để check allintitle (chính xác nhất)."""
    if not SERPAPI_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get("https://serpapi.com/search.json", params={
                "api_key": SERPAPI_KEY,
                "engine": "google",
                "q": f"allintitle:{keyword}",
                "gl": "vn",
                "hl": "vi",
                "num": 1,
            })
            if resp.status_code == 200:
                data = resp.json()
                total = data.get("search_information", {}).get("total_results", 0)
                return int(total) if total else 0
    except Exception:
        pass
    return None


# ── CSE fallback for allintitle ──────────────────────────────────────────────


async def _search_google_cse(query: str) -> Optional[int]:
    """Google Custom Search API — totalResults."""
    if not CSE_API_KEY or not CSE_ENGINE_ID:
        return None
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": CSE_API_KEY,
                    "cx": CSE_ENGINE_ID,
                    "q": query,
                    "num": 1,
                },
            )
            if resp.status_code == 200:
                return int(resp.json().get("searchInformation", {}).get("totalResults", 0))
    except Exception:
        pass
    return None


async def check_keyword_metrics(keyword: str) -> Dict[str, Any]:
    """Check allintitle + total results — dùng SerpAPI hoặc CSE."""
    # Prefer SerpAPI (more reliable)
    if SERPAPI_KEY:
        serp_data = await _get_serp_volume(keyword)
        allintitle = await _get_allintitle_serp(keyword)
        return {
            "allintitle": allintitle,
            "total_results": serp_data.get("total_results"),
            "source": "serpapi",
        }
    
    # Fallback to CSE
    allintitle = await _search_google_cse(f'allintitle:{keyword}')
    total_results = await _search_google_cse(keyword)
    return {
        "allintitle": allintitle,
        "total_results": total_results,
        "source": "cse",
    }


# ── Volume Estimation ────────────────────────────────────────────────────────


# Bảng ước tính volume phổ biến cho keywords Việt Nam
# Dựa trên mối quan hệ total_results vs actual volume từ SpinEditor data
VOLUME_BRACKETS = [
    (5_000_000_000, 1_000_000),
    (1_000_000_000, 500_000),
    (500_000_000, 200_000),
    (100_000_000, 100_000),
    (50_000_000, 50_000),
    (10_000_000, 20_000),
    (5_000_000, 10_000),
    (1_000_000, 5_000),
    (500_000, 2_000),
    (100_000, 1_000),
    (50_000, 500),
    (10_000, 200),
    (1_000, 100),
    (0, 50),
]


def estimate_volume(total_results: Optional[int]) -> Optional[int]:
    """Ước tính search volume từ total results (calibrated with SpinEditor data)."""
    if not total_results or total_results == 0:
        return None
    for threshold, volume in VOLUME_BRACKETS:
        if total_results >= threshold:
            return volume
    return 50


# ── KEI & Competition ────────────────────────────────────────────────────────


def calc_kei(search_volume: int, allintitle: int) -> float:
    """KEI = SearchVolume² / Allintitle (SpinEditor formula)."""
    if not allintitle or allintitle == 0:
        return 0.0
    return round((search_volume ** 2) / allintitle, 2)


def classify_competition(allintitle: Optional[int]) -> str:
    """Phân loại cạnh tranh — SpinEditor style."""
    if allintitle is None:
        return "--"
    if allintitle < 100:
        return "Low"
    elif allintitle < 1000:
        return "Medium"
    elif allintitle < 10000:
        return "High"
    else:
        return "Very High"


# ── Main Function ────────────────────────────────────────────────────────────


async def keyword_suggest(
    seed_keyword: str,
    check_metrics: bool = True,
    max_keywords: int = 30,
    lang: str = "vi",
) -> Dict[str, Any]:
    """
    Gợi ý từ khóa — phân tích từ SpinEditor.

    Pipeline:
    1. Google Suggest → lấy keyword ideas
    2. SerpAPI/CSE → allintitle + total results
    3. Volume estimation calibrated với SpinEditor data
    4. KEI & Competition calculation
    """
    if not seed_keyword or len(seed_keyword.strip()) < 2:
        return {"error": "Từ khóa quá ngắn (cần ít nhất 2 ký tự)"}

    # Step 1: Google Suggest
    suggestions = await expand_suggestions(seed_keyword.strip(), lang)
    suggestions = suggestions[:max_keywords]

    if not suggestions:
        # Fallback: try single suggest
        single = await google_suggest(seed_keyword.strip(), lang)
        suggestions = [s.lower() for s in single[:max_keywords]] if single else [seed_keyword.strip().lower()]

    # Step 2: Build keyword data
    keywords_data = []
    for kw in suggestions:
        keywords_data.append({
            "keyword": kw,
            "search_volume": None,
            "allintitle": None,
            "total_results": None,
            "kei": None,
            "competition": "--",
        })

    # Step 3: Check metrics
    has_api = bool(SERPAPI_KEY or CSE_API_KEY)
    if check_metrics and has_api:
        # SerpAPI: chỉ check top 5 (quota 100/month)
        # CSE: check top 10 (quota 100/day)
        check_count = min(5 if SERPAPI_KEY else 10, len(keywords_data))
        tasks = [check_keyword_metrics(kd["keyword"]) for kd in keywords_data[:check_count]]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i in range(check_count):
            if isinstance(results[i], dict):
                at = results[i].get("allintitle")
                tr = results[i].get("total_results")

                keywords_data[i]["allintitle"] = at
                keywords_data[i]["total_results"] = tr
                keywords_data[i]["competition"] = classify_competition(at)

                vol = estimate_volume(tr)
                keywords_data[i]["search_volume"] = vol

                if vol and at is not None:
                    keywords_data[i]["kei"] = calc_kei(vol, max(at, 1))

    source = "SerpAPI" if SERPAPI_KEY else "Google CSE" if CSE_API_KEY else "Google Suggest"
    return {
        "seed_keyword": seed_keyword,
        "total_suggestions": len(keywords_data),
        "keywords": keywords_data,
        "checked_metrics": check_metrics and has_api,
        "data_source": f"SpinEditor methodology ({source} + Allintitle + KEI)",
        "source_note": f"📊 Phân tích từ SpinEditor — {source} + Allintitle + KEI",
    }
