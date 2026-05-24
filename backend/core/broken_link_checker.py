"""
Broken Link Checker — SEO Tools

Scans a website for broken links:
- Crawls the starting URL's HTML
- Extracts <a href>, <img src>, <link href>, <script src>
- Classifies links as internal / external
- Checks HTTP status codes in parallel (async + httpx)
- Caps at max_links unique URLs for speed
- Returns report with broken links, status codes, source info
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (compatible; AI-Marketing-Hub/1.0; BrokenLinkChecker)"
DEFAULT_MAX_LINKS = 100
CONCURRENCY_LIMIT = 10  # Parallel HTTP requests


async def check_broken_links(
    url: str,
    max_links: int = DEFAULT_MAX_LINKS,
) -> Dict[str, Any]:
    """
    Scan a page for broken links.

    Args:
        url: Starting URL to crawl.
        max_links: Maximum unique links to check (default 100).

    Returns:
        Dict with broken_links, summary, all_links details.
    """
    start_time = time.time()

    # ── 1. Fetch the starting page ─────────────────────────────────────
    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            resp = await client.get(url)
    except httpx.TimeoutException:
        return _error_result(url, "Timeout khi tải trang. Thử lại sau.")
    except httpx.RequestError as exc:
        return _error_result(url, f"Không thể truy cập trang: {exc}")

    if resp.status_code >= 400:
        return _error_result(url, f"Trang trả về HTTP {resp.status_code}.")

    html = resp.text
    base_domain = urlparse(url).netloc

    # ── 2. Extract all links from HTML ─────────────────────────────────
    soup = BeautifulSoup(html, "lxml")
    raw_links = _extract_links(soup, url)

    # Deduplicate
    seen: Set[str] = set()
    unique_links: List[Dict[str, str]] = []
    for link in raw_links:
        if link["url"] not in seen:
            seen.add(link["url"])
            unique_links.append(link)

    # Classify internal/external
    for link in unique_links:
        parsed = urlparse(link["url"])
        link["type"] = "internal" if parsed.netloc == base_domain else "external"

    total_found = len(unique_links)
    links_to_check = unique_links[:max_links]

    # ── 3. Check HTTP status for each link ─────────────────────────────
    checked = await _check_links_parallel(links_to_check)

    # ── 4. Classify results ────────────────────────────────────────────
    broken: List[Dict[str, Any]] = []
    redirected: List[Dict[str, Any]] = []
    ok: List[Dict[str, Any]] = []

    for item in checked:
        status = item["status"]
        if status == 0 or status >= 400:
            broken.append(item)
        elif 300 <= status < 400:
            redirected.append(item)
        else:
            ok.append(item)

    duration = round(time.time() - start_time, 2)

    internal_broken = [b for b in broken if b.get("type") == "internal"]
    external_broken = [b for b in broken if b.get("type") == "external"]

    return {
        "url": url,
        "duration_seconds": duration,
        "summary": {
            "total_links_found": total_found,
            "total_checked": len(links_to_check),
            "broken_count": len(broken),
            "redirected_count": len(redirected),
            "ok_count": len(ok),
            "internal_broken": len(internal_broken),
            "external_broken": len(external_broken),
        },
        "broken_links": broken,
        "redirected_links": redirected[:10],  # Top 10 redirects
        "health_score": _health_score(len(ok), len(broken), len(links_to_check)),
        "recommendations": _build_recommendations(broken, redirected),
    }


# ── Link extraction ───────────────────────────────────────────────────────


def _extract_links(soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
    """Extract all resource links from parsed HTML."""
    links: List[Dict[str, str]] = []

    # <a href="...">
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if _should_skip(href):
            continue
        links.append({
            "url": urljoin(base_url, href),
            "source_tag": "a",
            "anchor_text": tag.get_text(strip=True)[:80] or "",
        })

    # <img src="...">
    for tag in soup.find_all("img", src=True):
        src = tag["src"].strip()
        if _should_skip(src):
            continue
        links.append({
            "url": urljoin(base_url, src),
            "source_tag": "img",
            "anchor_text": tag.get("alt", "")[:80],
        })

    # <link href="..."> (CSS, icons, etc.)
    for tag in soup.find_all("link", href=True):
        href = tag["href"].strip()
        if _should_skip(href):
            continue
        links.append({
            "url": urljoin(base_url, href),
            "source_tag": "link",
            "anchor_text": tag.get("rel", [""])[0] if tag.get("rel") else "",
        })

    # <script src="...">
    for tag in soup.find_all("script", src=True):
        src = tag["src"].strip()
        if _should_skip(src):
            continue
        links.append({
            "url": urljoin(base_url, src),
            "source_tag": "script",
            "anchor_text": "",
        })

    return links


def _should_skip(href: str) -> bool:
    """Skip non-HTTP links."""
    if not href:
        return True
    lower = href.lower()
    return any(lower.startswith(p) for p in (
        "#", "javascript:", "mailto:", "tel:", "data:", "blob:",
    ))


# ── Parallel HTTP checking ────────────────────────────────────────────────


async def _check_links_parallel(
    links: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    """Check HTTP status for each link with bounded concurrency."""
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    results: List[Dict[str, Any]] = []

    async with httpx.AsyncClient(
        timeout=10,
        follow_redirects=False,  # We want to detect redirects
        headers={"User-Agent": USER_AGENT},
    ) as client:

        async def _check_one(link: Dict[str, str]) -> Dict[str, Any]:
            async with semaphore:
                try:
                    resp = await client.head(link["url"])
                    status = resp.status_code
                    # Some servers reject HEAD, fall back to GET
                    if status == 405:
                        resp = await client.get(link["url"])
                        status = resp.status_code
                    return {**link, "status": status}
                except httpx.TimeoutException:
                    return {**link, "status": 0, "error": "Timeout"}
                except httpx.RequestError as exc:
                    return {**link, "status": 0, "error": str(exc)[:100]}

        tasks = [_check_one(link) for link in links]
        results = await asyncio.gather(*tasks)

    return list(results)


# ── Scoring & recommendations ─────────────────────────────────────────────


def _health_score(ok: int, broken: int, total: int) -> Dict[str, Any]:
    """Compute a link health score 0-100."""
    if total == 0:
        return {"score": 100, "grade": "A", "label": "Không có link để kiểm tra"}

    pct_ok = ok / total * 100
    score = round(pct_ok)

    if score >= 95:
        grade, label = "A", "Xuất sắc"
    elif score >= 85:
        grade, label = "B", "Tốt"
    elif score >= 70:
        grade, label = "C", "Trung bình"
    elif score >= 50:
        grade, label = "D", "Cần cải thiện"
    else:
        grade, label = "F", "Yếu"

    return {"score": score, "grade": grade, "label": label}


def _build_recommendations(
    broken: List[Dict],
    redirected: List[Dict],
) -> List[str]:
    """Generate actionable recommendations."""
    recs: List[str] = []

    if broken:
        internal_404 = [b for b in broken if b.get("type") == "internal" and b.get("status") == 404]
        external_dead = [b for b in broken if b.get("type") == "external"]

        if internal_404:
            recs.append(
                f"Sửa {len(internal_404)} link nội bộ trả về 404. "
                "Cập nhật href hoặc tạo redirect 301."
            )
        if external_dead:
            recs.append(
                f"{len(external_dead)} link ngoài bị hỏng. "
                "Xóa hoặc thay bằng link hoạt động."
            )

    if len(redirected) > 5:
        recs.append(
            f"{len(redirected)} link có redirect. "
            "Cập nhật href sang URL đích cuối để giảm redirect chain."
        )

    if not broken and not redirected:
        recs.append("Tất cả link hoạt động tốt. Tiếp tục kiểm tra định kỳ.")

    return recs


def _error_result(url: str, message: str) -> Dict[str, Any]:
    """Standardised error response."""
    return {
        "url": url,
        "duration_seconds": 0,
        "summary": {
            "total_links_found": 0,
            "total_checked": 0,
            "broken_count": 0,
            "redirected_count": 0,
            "ok_count": 0,
            "internal_broken": 0,
            "external_broken": 0,
        },
        "broken_links": [],
        "redirected_links": [],
        "health_score": {"score": 0, "grade": "N/A", "label": message},
        "recommendations": [message],
        "error": message,
    }
