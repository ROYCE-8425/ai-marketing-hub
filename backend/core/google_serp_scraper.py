"""
SERP Scraper — Phase 9 (Upgraded: Google Custom Search API)

Strategy:
1. DataForSEO API (if configured) — most reliable, premium
2. Google Custom Search JSON API (if configured) — official Google results
3. DuckDuckGo HTML scraping via lite.duckduckgo.com — free fallback
4. Mock data with clear Vietnamese notice

All searches are async-safe and never hang.
"""

import asyncio
import re
import sys
import json
import subprocess
from typing import Any, Dict, List
from urllib.parse import urlparse, quote_plus
import os

import httpx


LOCATION_MAP = {
    "vn": {"gl": "vn", "hl": "vi", "kl": "vn-vi", "label": "Việt Nam"},
    "us": {"gl": "us", "hl": "en", "kl": "us-en", "label": "Hoa Kỳ"},
    "uk": {"gl": "uk", "hl": "en", "kl": "uk-en", "label": "Anh"},
    "au": {"gl": "au", "hl": "en", "kl": "au-en", "label": "Úc"},
    "in": {"gl": "in", "hl": "en", "kl": "in-en", "label": "Ấn Độ"},
    "sg": {"gl": "sg", "hl": "en", "kl": "sg-en", "label": "Singapore"},
    "jp": {"gl": "jp", "hl": "ja", "kl": "jp-jp", "label": "Nhật Bản"},
}


def _mock_serp(keyword: str, loc_label: str) -> Dict[str, Any]:
    """Return realistic Vietnamese mock SERP data."""
    kw = keyword.lower()
    slug = kw.replace(" ", "-")
    mock_results = [
        {"position": i + 1, "title": t, "url": u, "domain": d, "snippet": s, "breadcrumb": ""}
        for i, (t, u, d, s) in enumerate([
            (f"Top 10 {keyword} - Hướng dẫn đầy đủ 2025", f"https://www.techradar.com/best/{slug}", "techradar.com", f"Chuyên gia đánh giá {kw} tốt nhất. So sánh tính năng và giá cả."),
            (f"{keyword} - Đánh giá chuyên sâu", f"https://www.pcmag.com/picks/{slug}", "pcmag.com", f"PCMag đánh giá và xếp hạng {kw}. Tìm giải pháp phù hợp."),
            (f"{keyword} tốt nhất (Xếp hạng)", f"https://www.forbes.com/advisor/{slug}", "forbes.com", f"Forbes Advisor xếp hạng {kw} dựa trên tính năng và giá."),
            (f"{keyword}: Hướng dẫn mua hàng", f"https://www.g2.com/categories/{slug}", "g2.com", f"So sánh {kw} dựa trên đánh giá người dùng thực."),
            (f"Cách chọn {keyword} phù hợp", "https://www.youtube.com/watch?v=example", "youtube.com", f"Video hướng dẫn chọn {kw} phù hợp nhất."),
            (f"{keyword} - Wikipedia", f"https://vi.wikipedia.org/wiki/{slug}", "wikipedia.org", f"{keyword} là thuật ngữ dùng để chỉ..."),
            (f"Reddit - {keyword} tốt nhất?", f"https://www.reddit.com/r/best_{slug}", "reddit.com", f"Cộng đồng đề xuất {kw} tốt nhất 2025."),
            (f"So sánh {keyword} 2025", f"https://www.capterra.com/compare/{slug}", "capterra.com", f"So sánh chi tiết các giải pháp {kw}."),
            (f"{keyword} giá rẻ cho doanh nghiệp", f"https://www.hostinger.com/{slug}", "hostinger.com", f"Bắt đầu với {kw} chỉ từ 59.000đ/tháng."),
            (f"{keyword} - Đánh giá Trustpilot", f"https://www.trustpilot.com/categories/{slug}", "trustpilot.com", f"Đọc đánh giá thực từ khách hàng về {kw}."),
        ])
    ]
    return {
        "keyword": keyword,
        "location": loc_label,
        "organic_results": mock_results[:10],
        "serp_features": ["video_carousel", "knowledge_panel", "people_also_ask"],
        "total_results": 10,
        "results_count": 10,
        "source": "mock_serp",
        "note": "⚠️ Dữ liệu mẫu — Cấu hình GOOGLE_SEARCH_API_KEY + GOOGLE_SEARCH_CX hoặc DataForSEO để có dữ liệu Google thật.",
    }


async def _google_custom_search(keyword: str, location: str, num_results: int) -> List[Dict]:
    """
    Use Google Custom Search JSON API.
    Free: 100 queries/day. Paid: $5 per 1000 queries.
    Requires: GOOGLE_SEARCH_API_KEY + GOOGLE_SEARCH_CX env vars.

    Docs: https://developers.google.com/custom-search/v1/overview
    """
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_SEARCH_CX")
    if not api_key or not cx:
        return []

    loc = LOCATION_MAP.get(location.lower(), LOCATION_MAP["vn"])
    # Google CSE supports max 10 results per request
    num = min(num_results, 10)

    params = {
        "key": api_key,
        "cx": cx,
        "q": keyword,
        "num": num,
        "gl": loc["gl"],
        "hl": loc["hl"],
    }

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

        items = data.get("items", [])
        results = []
        for i, item in enumerate(items, 1):
            link = item.get("link", "")
            try:
                domain = urlparse(link).netloc.replace("www.", "")
            except Exception:
                domain = ""
            results.append({
                "position": i,
                "title": item.get("title", ""),
                "url": link,
                "domain": domain,
                "snippet": item.get("snippet", ""),
                "breadcrumb": item.get("formattedUrl", ""),
            })
        return results
    except Exception:
        return []


def _ddg_subprocess(keyword: str, region: str, max_results: int) -> List[Dict]:
    """Run DuckDuckGo search in a subprocess with strict timeout."""
    script = f'''
import json, warnings, sys
warnings.filterwarnings("ignore")
try:
    from duckduckgo_search import DDGS
    with DDGS() as ddgs:
        results = list(ddgs.text({json.dumps(keyword)}, region={json.dumps(region)}, max_results={max_results}))
        print(json.dumps(results, ensure_ascii=False))
except Exception as e:
    print(json.dumps([]))
'''
    try:
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, timeout=12,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout.strip())
            if isinstance(data, list) and len(data) > 0:
                return data
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        pass
    return []


class GoogleSerpScraper:
    """SERP scraper with multiple fallbacks: Google API → DuckDuckGo → Mock."""

    async def search(self, keyword: str, location: str = "vn", num_results: int = 10) -> Dict[str, Any]:
        loc = LOCATION_MAP.get(location.lower(), LOCATION_MAP["vn"])
        kl = loc.get("kl", "vn-vi")
        num = max(5, min(20, num_results))

        # Strategy 1: Google Custom Search API (official Google results)
        google_results = await _google_custom_search(keyword, location, num)
        if google_results:
            features = self._detect_features(google_results)
            return {
                "keyword": keyword,
                "location": loc.get("label", ""),
                "organic_results": google_results,
                "serp_features": features,
                "total_results": len(google_results),
                "results_count": len(google_results),
                "source": "google_custom_search",
            }

        # Strategy 2: DuckDuckGo fallback (free, no key needed)
        try:
            raw = await asyncio.wait_for(
                asyncio.to_thread(_ddg_subprocess, keyword, kl, num),
                timeout=15.0,
            )
            if raw:
                return self._format_ddg(raw, keyword, loc)
        except Exception:
            pass

        # Strategy 3: Mock data
        result = _mock_serp(keyword, loc.get("label", ""))
        result["error"] = "Search engine không phản hồi — hiển thị dữ liệu mẫu. Cấu hình GOOGLE_SEARCH_API_KEY + GOOGLE_SEARCH_CX để có kết quả Google thật."
        return result

    def _detect_features(self, results: List[Dict]) -> List[str]:
        """Detect SERP features from result domains."""
        features = []
        domains = [r.get("domain", "") for r in results]
        if any("youtube.com" in d for d in domains):
            features.append("video_carousel")
        if any("wikipedia.org" in d for d in domains):
            features.append("knowledge_panel")
        return features

    def _format_ddg(self, raw: List[Dict], keyword: str, loc: Dict) -> Dict[str, Any]:
        organic = []
        for i, item in enumerate(raw, 1):
            href = item.get("href", "") or item.get("link", "")
            title = item.get("title", "")
            body = item.get("body", "") or item.get("snippet", "")
            if not href or not title:
                continue
            try:
                domain = urlparse(href).netloc.replace("www.", "")
            except Exception:
                domain = ""
            organic.append({
                "position": i, "title": title, "url": href,
                "domain": domain, "snippet": body, "breadcrumb": "",
            })

        features = self._detect_features(organic)

        return {
            "keyword": keyword,
            "location": loc.get("label", ""),
            "organic_results": organic,
            "serp_features": features,
            "total_results": len(organic),
            "results_count": len(organic),
            "source": "duckduckgo_live",
        }


async def scrape_google_serp(keyword: str, location: str = "vn", num_results: int = 10) -> Dict[str, Any]:
    return await GoogleSerpScraper().search(keyword, location, num_results)
