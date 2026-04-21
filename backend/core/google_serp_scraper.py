"""
SERP Scraper — Phase 8

Uses duckduckgo-search library with a 10-second timeout.
If the search times out or fails, returns mock SERP data so the UI never hangs.
"""

import asyncio
from typing import Any, Dict, List
from urllib.parse import urlparse


LOCATION_MAP = {
    "vn": {"region": "vn-vi", "label": "Việt Nam"},
    "us": {"region": "us-en", "label": "United States"},
    "uk": {"region": "uk-en", "label": "United Kingdom"},
    "au": {"region": "au-en", "label": "Australia"},
    "in": {"region": "in-en", "label": "India"},
    "sg": {"region": "sg-en", "label": "Singapore"},
    "jp": {"region": "jp-jp", "label": "Japan"},
}


def _ddg_sync(keyword: str, region: str, max_results: int) -> List[Dict]:
    """Sync DuckDuckGo search — runs in thread."""
    from duckduckgo_search import DDGS
    with DDGS() as ddgs:
        return list(ddgs.text(keyword, region=region, max_results=max_results))


def _mock_serp(keyword: str, loc_label: str) -> Dict[str, Any]:
    """Return realistic mock SERP data when network is unavailable."""
    kw = keyword.lower()
    mock_results = [
        {"position": 1, "title": f"Top 10 {keyword} - Complete Guide 2025", "url": "https://www.techradar.com/best/" + kw.replace(" ", "-"), "domain": "techradar.com", "snippet": f"Our experts tested the best {kw} services. Compare features, pricing and performance.", "breadcrumb": ""},
        {"position": 2, "title": f"{keyword} - Expert Reviews & Comparisons", "url": "https://www.pcmag.com/picks/" + kw.replace(" ", "-"), "domain": "pcmag.com", "snippet": f"PCMag editors rate and review the top {kw} options. Find the right solution.", "breadcrumb": ""},
        {"position": 3, "title": f"Best {keyword} (Reviewed & Ranked)", "url": "https://www.forbes.com/advisor/" + kw.replace(" ", "-"), "domain": "forbes.com", "snippet": f"Forbes Advisor ranks the best {kw} based on features, pricing, ease of use and more.", "breadcrumb": ""},
        {"position": 4, "title": f"{keyword}: Ultimate Buyer's Guide", "url": "https://www.g2.com/categories/" + kw.replace(" ", "-"), "domain": "g2.com", "snippet": f"Compare {kw} based on verified user reviews. See ratings, features and pricing.", "breadcrumb": ""},
        {"position": 5, "title": f"How to Choose the Right {keyword}", "url": "https://www.youtube.com/watch?v=example", "domain": "youtube.com", "snippet": f"In this video we break down everything you need to know about choosing {kw}.", "breadcrumb": ""},
        {"position": 6, "title": f"{keyword} - Wikipedia", "url": f"https://en.wikipedia.org/wiki/{kw.replace(' ', '_')}", "domain": "wikipedia.org", "snippet": f"{keyword} refers to services and platforms that provide...", "breadcrumb": ""},
        {"position": 7, "title": f"Reddit - Best {keyword}?", "url": f"https://www.reddit.com/r/webhosting/comments/best_{kw.replace(' ', '_')}", "domain": "reddit.com", "snippet": f"What's the best {kw} in 2025? Here's what the community recommends.", "breadcrumb": ""},
        {"position": 8, "title": f"{keyword} Comparison Chart 2025", "url": "https://www.capterra.com/compare/" + kw.replace(" ", "-"), "domain": "capterra.com", "snippet": f"Side-by-side comparison of top {kw} solutions. Filter by features and price.", "breadcrumb": ""},
        {"position": 9, "title": f"Affordable {keyword} for Small Business", "url": "https://www.hostinger.com/" + kw.replace(" ", "-"), "domain": "hostinger.com", "snippet": f"Get started with {kw} from $2.99/mo. 30-day money-back guarantee.", "breadcrumb": ""},
        {"position": 10, "title": f"{keyword} - Trustpilot Reviews", "url": "https://www.trustpilot.com/categories/" + kw.replace(" ", "-"), "domain": "trustpilot.com", "snippet": f"Read real customer reviews of {kw} companies. Find the most trusted provider.", "breadcrumb": ""},
    ]
    return {
        "keyword": keyword,
        "location": loc_label,
        "organic_results": mock_results[:10],
        "serp_features": ["video_carousel", "knowledge_panel", "people_also_ask"],
        "total_results": 10,
        "results_count": 10,
        "source": "mock_serp",
        "note": "⚠️ Dữ liệu mẫu — mạng server không kết nối được search engine. Thử lại sau hoặc cấu hình DataForSEO API key.",
    }


class GoogleSerpScraper:
    """Fetches real search results via DuckDuckGo with timeout + mock fallback."""

    async def search(self, keyword: str, location: str = "vn", num_results: int = 10) -> Dict[str, Any]:
        loc = LOCATION_MAP.get(location.lower(), LOCATION_MAP["vn"])
        num = max(5, min(20, num_results))
        region = loc.get("region", "us-en")

        try:
            raw = await asyncio.wait_for(
                asyncio.to_thread(_ddg_sync, keyword, region, num),
                timeout=10.0,
            )
            return self._format(raw, keyword, loc)
        except asyncio.TimeoutError:
            result = _mock_serp(keyword, loc.get("label", ""))
            result["error"] = "Search timed out — showing mock data"
            return result
        except Exception as exc:
            result = _mock_serp(keyword, loc.get("label", ""))
            result["error"] = f"Search failed: {str(exc)[:100]} — showing mock data"
            return result

    def _format(self, raw: List[Dict], keyword: str, loc: Dict) -> Dict[str, Any]:
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

        features = []
        domains = [r["domain"] for r in organic]
        if any("youtube.com" in d for d in domains): features.append("video_carousel")
        if any("wikipedia.org" in d for d in domains): features.append("knowledge_panel")

        return {
            "keyword": keyword,
            "location": loc.get("label", ""),
            "organic_results": organic,
            "serp_features": features,
            "total_results": len(organic),
            "results_count": len(organic),
            "source": "duckduckgo_search",
        }


async def scrape_google_serp(keyword: str, location: str = "vn", num_results: int = 10) -> Dict[str, Any]:
    return await GoogleSerpScraper().search(keyword, location, num_results)
