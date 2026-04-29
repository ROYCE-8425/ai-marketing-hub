"""
Backlink Analyzer — Phase 14

Analyzes backlinks for a website:
- Extracts internal/external links
- Checks link quality signals
- Identifies referring domains
- Suggests link building opportunities
"""

import re
import asyncio
from typing import Any, Dict, List
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


async def _fetch_page(url: str) -> str:
    """Fetch HTML content."""
    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; AI-Marketing-Hub/1.0; Backlink Analyzer)"
            })
            return resp.text if resp.status_code == 200 else ""
    except Exception:
        return ""


def _extract_links(html: str, base_url: str) -> Dict[str, List[Dict[str, str]]]:
    """Extract and categorize all links from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    domain = urlparse(base_url).netloc
    internal = []
    external = []

    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        if not href or href.startswith("#") or href.startswith("javascript:") or href.startswith("tel:") or href.startswith("mailto:"):
            continue

        full_url = urljoin(base_url, href)
        anchor = a.get_text(strip=True)[:80] or "[no text]"
        rel = a.get("rel", [])
        nofollow = "nofollow" in rel if rel else False

        link_data = {
            "url": full_url,
            "anchor": anchor,
            "nofollow": nofollow,
        }

        if domain in urlparse(full_url).netloc:
            internal.append(link_data)
        else:
            link_data["domain"] = urlparse(full_url).netloc
            external.append(link_data)

    return {"internal": internal, "external": external}


def _analyze_link_quality(links: List[Dict[str, str]]) -> Dict[str, Any]:
    """Score link quality based on heuristics."""
    if not links:
        return {"score": 0, "total": 0, "quality": "none"}

    total = len(links)
    dofollow = sum(1 for l in links if not l.get("nofollow"))
    nofollow = total - dofollow

    # Anchor text quality
    branded = sum(1 for l in links if len(l.get("anchor", "")) > 3 and l["anchor"] != "[no text]")
    generic = sum(1 for l in links if l.get("anchor", "") in ["click here", "đọc thêm", "xem thêm", "here", "link"])

    # Domain diversity
    unique_domains = len(set(l.get("domain", "") for l in links if l.get("domain")))

    # Quality score (0-100)
    score = 0
    if total > 0:
        score += min(25, (dofollow / total) * 25) if total > 0 else 0
        score += min(25, (branded / total) * 25) if total > 0 else 0
        score += min(25, unique_domains * 5)
        score += min(25, total * 2)

    score = min(100, round(score))

    return {
        "score": score,
        "total": total,
        "dofollow": dofollow,
        "nofollow": nofollow,
        "unique_domains": unique_domains,
        "branded_anchors": branded,
        "generic_anchors": generic,
        "quality": "good" if score >= 60 else "fair" if score >= 30 else "poor",
    }


def _get_referring_domains(external_links: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Group external links by referring domain."""
    domain_map: Dict[str, Dict[str, Any]] = {}

    for link in external_links:
        domain = link.get("domain", "unknown")
        if domain not in domain_map:
            domain_map[domain] = {
                "domain": domain,
                "links": 0,
                "dofollow": 0,
                "nofollow": 0,
                "anchors": [],
            }
        domain_map[domain]["links"] += 1
        if link.get("nofollow"):
            domain_map[domain]["nofollow"] += 1
        else:
            domain_map[domain]["dofollow"] += 1
        if link.get("anchor") and link["anchor"] != "[no text]" and link["anchor"] not in domain_map[domain]["anchors"]:
            domain_map[domain]["anchors"].append(link["anchor"][:40])

    # Sort by link count
    domains = sorted(domain_map.values(), key=lambda x: x["links"], reverse=True)
    # Limit anchors
    for d in domains:
        d["anchors"] = d["anchors"][:3]
    return domains[:30]


def _generate_suggestions(internal_links: List[Dict], external_links: List[Dict], url: str) -> List[str]:
    """Generate link building suggestions."""
    suggestions = []

    if len(external_links) < 5:
        suggestions.append("Xây dựng thêm liên kết từ website bên ngoài (guest posting, PR, directories)")

    nofollow_ratio = sum(1 for l in external_links if l.get("nofollow")) / max(1, len(external_links))
    if nofollow_ratio > 0.5:
        suggestions.append("Tỷ lệ nofollow quá cao — tìm kiếm backlinks dofollow chất lượng")

    unique_domains = len(set(l.get("domain", "") for l in external_links))
    if unique_domains < 3:
        suggestions.append("Đa dạng hóa nguồn backlink — nhận link từ nhiều domain khác nhau")

    if len(internal_links) < 10:
        suggestions.append("Tăng số internal links — kết nối các trang liên quan với nhau")

    generic_count = sum(1 for l in internal_links + external_links if l.get("anchor", "") in ["click here", "đọc thêm", "xem thêm", "here", "link", "[no text]"])
    if generic_count > 5:
        suggestions.append(f"Thay {generic_count} anchor text chung chung (click here, xem thêm) bằng keyword cụ thể")

    # Always useful
    suggestions.append("Submit website lên các thư mục doanh nghiệp địa phương (Google Business, Yelp VN)")
    suggestions.append("Viết bài guest post trên các blog ngành ô tô, xe hơi")

    return suggestions[:8]


async def analyze_backlinks(url: str) -> Dict[str, Any]:
    """
    Full backlink analysis for a URL.

    Note: This analyzes links ON the page (outbound), not links TO the page.
    For full backlink profiling, DataForSEO or Ahrefs API would be needed.
    """
    html = await _fetch_page(url)
    if not html:
        return {"error": f"Không thể truy cập {url}"}

    links = _extract_links(html, url)
    internal = links["internal"]
    external = links["external"]

    internal_quality = _analyze_link_quality(internal)
    external_quality = _analyze_link_quality(external)
    referring_domains = _get_referring_domains(external)
    suggestions = _generate_suggestions(internal, external, url)

    # Overall score
    overall = round((internal_quality["score"] * 0.4 + external_quality["score"] * 0.6))

    if overall >= 70: grade = "A"
    elif overall >= 50: grade = "B"
    elif overall >= 30: grade = "C"
    else: grade = "D"

    return {
        "url": url,
        "overall_score": overall,
        "grade": grade,
        "internal_links": {
            "total": len(internal),
            "quality": internal_quality,
            "sample": internal[:15],
        },
        "external_links": {
            "total": len(external),
            "quality": external_quality,
            "sample": external[:15],
        },
        "referring_domains": referring_domains,
        "total_domains": len(referring_domains),
        "suggestions": suggestions,
    }
