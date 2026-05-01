"""
Technical SEO Scanner — Phase 16

Scans a website for technical SEO issues:
- Page speed / performance metrics
- Mobile friendliness (viewport, responsive)
- Broken links (404 detection)
- Sitemap.xml / robots.txt validation
- SSL / HTTPS check
- Meta tags validation
- Redirect chains
- Image optimization
"""

import re
import time
import asyncio
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


async def _fetch_page(url: str, timeout: int = 15) -> Dict[str, Any]:
    """Fetch a page and measure load time."""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; AI-Marketing-Hub/1.0; TechSEO Scanner)"
            })
            load_time = round(time.time() - start, 2)
            return {
                "status": resp.status_code,
                "html": resp.text,
                "load_time": load_time,
                "final_url": str(resp.url),
                "redirects": len(resp.history),
                "headers": dict(resp.headers),
            }
    except Exception as e:
        return {"status": 0, "error": str(e), "load_time": round(time.time() - start, 2)}


def _check_meta_tags(soup: BeautifulSoup) -> Dict[str, Any]:
    """Validate meta tags."""
    issues = []
    score = 0

    # Title
    title = soup.find("title")
    title_text = title.get_text(strip=True) if title else ""
    if not title_text:
        issues.append({"severity": "critical", "message": "Thiếu thẻ <title>", "fix": "Thêm <title>Tiêu đề trang</title> vào <head>"})
    elif len(title_text) < 20:
        issues.append({"severity": "warning", "message": f"Title quá ngắn ({len(title_text)} ký tự)", "fix": "Title nên 50-60 ký tự"})
    elif len(title_text) > 65:
        issues.append({"severity": "warning", "message": f"Title quá dài ({len(title_text)} ký tự)", "fix": "Title nên dưới 60 ký tự"})
    else:
        score += 10

    # Meta description
    desc_meta = soup.find("meta", attrs={"name": "description"})
    desc = desc_meta.get("content", "") if desc_meta else ""
    if not desc:
        issues.append({"severity": "critical", "message": "Thiếu meta description", "fix": 'Thêm <meta name="description" content="..."> vào <head>'})
    elif len(desc) < 50:
        issues.append({"severity": "warning", "message": f"Meta description quá ngắn ({len(desc)} ký tự)", "fix": "Nên 120-160 ký tự"})
    elif len(desc) > 170:
        issues.append({"severity": "warning", "message": f"Meta description quá dài ({len(desc)} ký tự)", "fix": "Nên dưới 160 ký tự"})
    else:
        score += 10

    # Canonical
    canonical = soup.find("link", attrs={"rel": "canonical"})
    if not canonical:
        issues.append({"severity": "warning", "message": "Thiếu canonical URL", "fix": 'Thêm <link rel="canonical" href="URL"> vào <head>'})
    else:
        score += 5

    # Open Graph
    og_title = soup.find("meta", attrs={"property": "og:title"})
    og_desc = soup.find("meta", attrs={"property": "og:description"})
    og_image = soup.find("meta", attrs={"property": "og:image"})
    og_count = sum(1 for t in [og_title, og_desc, og_image] if t)
    if og_count < 3:
        missing = []
        if not og_title: missing.append("og:title")
        if not og_desc: missing.append("og:description")
        if not og_image: missing.append("og:image")
        issues.append({"severity": "info", "message": f"Thiếu Open Graph: {', '.join(missing)}", "fix": "Thêm OG tags để chia sẻ đẹp trên mạng xã hội"})
    else:
        score += 5

    return {"score": score, "max": 30, "title": title_text, "description": desc, "issues": issues}


def _check_headings(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check heading structure."""
    issues = []
    score = 0

    h1s = soup.find_all("h1")
    h2s = soup.find_all("h2")

    if not h1s:
        issues.append({"severity": "critical", "message": "Thiếu thẻ H1", "fix": "Mỗi trang cần đúng 1 thẻ <h1>"})
    elif len(h1s) > 1:
        issues.append({"severity": "warning", "message": f"Có {len(h1s)} thẻ H1 (nên chỉ có 1)", "fix": "Giữ 1 H1 duy nhất cho mỗi trang"})
    else:
        score += 10

    if h2s:
        score += 5
    else:
        issues.append({"severity": "info", "message": "Không có thẻ H2", "fix": "Chia nội dung thành các section với H2"})

    return {"score": score, "max": 15, "h1_count": len(h1s), "h2_count": len(h2s), "issues": issues}


def _check_images(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check image optimization."""
    issues = []
    score = 0

    images = soup.find_all("img")
    if not images:
        return {"score": 5, "max": 15, "total": 0, "issues": []}

    missing_alt = [img.get("src", "?")[:50] for img in images if not img.get("alt", "").strip()]
    large_images = [img.get("src", "?")[:50] for img in images if not img.get("loading")]
    no_dims = [img.get("src", "?")[:50] for img in images if not img.get("width") and not img.get("height")]

    alt_ratio = 1 - (len(missing_alt) / len(images)) if images else 1
    score += int(alt_ratio * 8)

    if missing_alt:
        issues.append({
            "severity": "warning",
            "message": f"{len(missing_alt)}/{len(images)} hình thiếu alt text",
            "fix": "Thêm alt text mô tả cho mỗi hình ảnh"
        })

    lazy_count = sum(1 for img in images if img.get("loading") == "lazy")
    if lazy_count < len(images) * 0.5 and len(images) > 3:
        issues.append({
            "severity": "info",
            "message": f"Chỉ {lazy_count}/{len(images)} hình có lazy loading",
            "fix": 'Thêm loading="lazy" cho hình ảnh dưới fold'
        })
    else:
        score += 4

    if no_dims and len(no_dims) > len(images) * 0.5:
        issues.append({
            "severity": "info",
            "message": f"{len(no_dims)} hình thiếu width/height",
            "fix": "Thêm width/height để tránh CLS"
        })
    else:
        score += 3

    return {"score": min(15, score), "max": 15, "total": len(images),
            "missing_alt": len(missing_alt), "lazy_loaded": lazy_count, "issues": issues}


def _check_mobile(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check mobile friendliness."""
    issues = []
    score = 0

    viewport = soup.find("meta", attrs={"name": "viewport"})
    if viewport:
        content = viewport.get("content", "")
        if "width=device-width" in content:
            score += 10
        else:
            issues.append({"severity": "warning", "message": "Viewport thiếu width=device-width", "fix": 'Thêm content="width=device-width, initial-scale=1"'})
    else:
        issues.append({"severity": "critical", "message": "Thiếu meta viewport", "fix": '<meta name="viewport" content="width=device-width, initial-scale=1">'})

    # Check for mobile-unfriendly elements
    text = str(soup)
    if "flash" in text.lower() or "<embed" in text.lower():
        issues.append({"severity": "warning", "message": "Phát hiện Flash/Embed", "fix": "Loại bỏ Flash, dùng HTML5"})
    else:
        score += 5

    return {"score": score, "max": 15, "has_viewport": bool(viewport), "issues": issues}


async def _check_links(soup: BeautifulSoup, base_url: str, max_check: int = 20) -> Dict[str, Any]:
    """Check for broken internal links."""
    issues = []
    links = soup.find_all("a", href=True)
    internal_links = []
    external_links = 0
    domain = urlparse(base_url).netloc

    for a in links:
        href = a.get("href", "")
        if href.startswith("#") or href.startswith("javascript:") or href.startswith("tel:") or href.startswith("mailto:"):
            continue
        full_url = urljoin(base_url, href)
        if domain in urlparse(full_url).netloc:
            internal_links.append(full_url)
        else:
            external_links += 1

    # Check a sample of internal links for 404
    broken = []
    checked = 0
    unique_links = list(set(internal_links))[:max_check]

    async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
        tasks = []
        for link in unique_links:
            tasks.append(client.head(link, headers={"User-Agent": "Mozilla/5.0 (compatible; AI-Marketing-Hub)"}))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for link, result in zip(unique_links, results):
            checked += 1
            if isinstance(result, Exception):
                broken.append({"url": link, "status": "error", "error": str(result)[:50]})
            elif result.status_code >= 400:
                broken.append({"url": link, "status": result.status_code})

    score = 10
    if broken:
        score = max(0, 10 - len(broken) * 2)
        issues.append({
            "severity": "critical" if len(broken) > 3 else "warning",
            "message": f"{len(broken)} link lỗi / tổng {checked} link kiểm tra",
            "fix": "Sửa hoặc xóa các link bị hỏng"
        })

    return {
        "score": score, "max": 10,
        "total_internal": len(internal_links), "total_external": external_links,
        "checked": checked, "broken": broken, "issues": issues
    }


async def _check_sitemap_robots(base_url: str) -> Dict[str, Any]:
    """Check sitemap.xml and robots.txt with detailed parsing."""
    issues = []
    score = 0
    domain_base = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
    robots_data: Dict[str, Any] = {}
    sitemap_data: Dict[str, Any] = {}

    async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
        # ── robots.txt ─────────────────────────────────────────────
        try:
            r = await client.get(f"{domain_base}/robots.txt")
            if r.status_code == 200 and len(r.text) > 10:
                score += 5
                has_robots = True
                # Parse robots.txt directives
                lines = r.text.strip().splitlines()
                disallow = [l.split(":", 1)[1].strip() for l in lines if l.lower().startswith("disallow:")]
                allow = [l.split(":", 1)[1].strip() for l in lines if l.lower().startswith("allow:")]
                sitemaps_ref = [l.split(":", 1)[1].strip() for l in lines if l.lower().startswith("sitemap:")]
                crawl_delay = next((l.split(":", 1)[1].strip() for l in lines if l.lower().startswith("crawl-delay:")), None)
                robots_data = {
                    "disallow_rules": disallow[:10],
                    "allow_rules": allow[:10],
                    "sitemap_refs": sitemaps_ref,
                    "crawl_delay": crawl_delay,
                    "total_lines": len(lines),
                }
                if not sitemaps_ref:
                    issues.append({"severity": "info", "message": "robots.txt không khai báo Sitemap URL", "fix": "Thêm Sitemap: https://domain.com/sitemap.xml vào robots.txt"})
                if any(d == "/" for d in disallow):
                    issues.append({"severity": "critical", "message": "robots.txt chặn toàn bộ trang (Disallow: /)", "fix": "Xóa dòng 'Disallow: /' nếu muốn Google index"})
                    score -= 5
            else:
                has_robots = False
                issues.append({"severity": "warning", "message": "robots.txt không tồn tại hoặc rỗng", "fix": "Tạo file robots.txt ở root domain"})
        except Exception:
            has_robots = False
            issues.append({"severity": "warning", "message": "Không thể truy cập robots.txt", "fix": "Tạo file robots.txt"})

        # ── sitemap.xml ────────────────────────────────────────────
        try:
            r = await client.get(f"{domain_base}/sitemap.xml")
            content = r.text.lower()
            if r.status_code == 200 and ("<url>" in content or "<sitemap>" in content):
                score += 5
                has_sitemap = True
                # Parse sitemap
                url_count = content.count("<url>")
                sitemap_count = content.count("<sitemap>")
                has_lastmod = "<lastmod>" in content
                is_index = sitemap_count > 0
                sitemap_data = {
                    "url_count": url_count,
                    "sitemap_count": sitemap_count,
                    "is_index": is_index,
                    "has_lastmod": has_lastmod,
                    "size_kb": round(len(r.text) / 1024, 1),
                }
                if not has_lastmod:
                    issues.append({"severity": "info", "message": "Sitemap thiếu <lastmod> dates", "fix": "Thêm lastmod để Google ưu tiên crawl trang mới"})
                if url_count > 50000:
                    issues.append({"severity": "warning", "message": f"Sitemap có {url_count} URLs (giới hạn 50,000)", "fix": "Chia thành sitemap index với nhiều sub-sitemaps"})
            else:
                has_sitemap = False
                issues.append({"severity": "warning", "message": "sitemap.xml không tồn tại", "fix": "Tạo sitemap.xml và submit lên Google Search Console"})
        except Exception:
            has_sitemap = False
            issues.append({"severity": "warning", "message": "Không thể truy cập sitemap.xml", "fix": "Tạo sitemap.xml"})

    return {
        "score": max(0, score), "max": 10,
        "has_robots": has_robots, "has_sitemap": has_sitemap,
        "robots_details": robots_data, "sitemap_details": sitemap_data,
        "issues": issues,
    }


def _check_performance(load_time: float, html: str, headers: dict) -> Dict[str, Any]:
    """Estimate performance metrics."""
    issues = []
    score = 0

    # Load time
    if load_time < 1.0:
        score += 5
    elif load_time < 2.0:
        score += 3
    elif load_time < 3.0:
        score += 1
        issues.append({"severity": "warning", "message": f"Trang tải chậm ({load_time}s)", "fix": "Tối ưu: nén hình, minify CSS/JS, CDN"})
    else:
        issues.append({"severity": "critical", "message": f"Trang tải rất chậm ({load_time}s)", "fix": "Cần tối ưu performance: nén, cache, CDN"})

    # Page size
    page_size_kb = len(html.encode()) / 1024
    if page_size_kb < 200:
        score += 3
    elif page_size_kb < 500:
        score += 1
    else:
        issues.append({"severity": "warning", "message": f"HTML quá nặng ({int(page_size_kb)}KB)", "fix": "Giảm kích thước HTML, loại bỏ code không cần"})

    # Compression
    encoding = headers.get("content-encoding", "")
    if "gzip" in encoding or "br" in encoding:
        score += 2
    else:
        issues.append({"severity": "info", "message": "Chưa bật Gzip/Brotli compression", "fix": "Bật compression trên server"})

    return {"score": score, "max": 10, "load_time": load_time,
            "page_size_kb": round(page_size_kb), "compressed": bool(encoding), "issues": issues}


def _check_security(url: str, headers: dict) -> Dict[str, Any]:
    """Check security headers."""
    issues = []
    score = 0

    if url.startswith("https"):
        score += 5
    else:
        issues.append({"severity": "critical", "message": "Trang không dùng HTTPS", "fix": "Cài SSL certificate, redirect HTTP → HTTPS"})

    security_headers = {
        "x-content-type-options": "X-Content-Type-Options",
        "x-frame-options": "X-Frame-Options",
        "strict-transport-security": "HSTS",
    }
    for header_key, label in security_headers.items():
        if header_key in {k.lower(): v for k, v in headers.items()}:
            score += 1

    if score < 7:
        issues.append({"severity": "info", "message": "Thiếu một số security headers", "fix": "Thêm X-Content-Type-Options, X-Frame-Options, HSTS"})

    return {"score": min(5, score), "max": 5, "https": url.startswith("https"), "issues": issues}


async def scan_technical_seo(url: str) -> Dict[str, Any]:
    """
    Full technical SEO scan.

    Returns score (0-100) with detailed breakdown.
    """
    # Fetch page
    page = await _fetch_page(url)
    if page.get("error"):
        return {"error": f"Không thể truy cập {url}: {page['error']}"}

    html = page.get("html", "")
    soup = BeautifulSoup(html, "html.parser")

    # Run all checks
    meta_result = _check_meta_tags(soup)
    heading_result = _check_headings(soup)
    image_result = _check_images(soup)
    mobile_result = _check_mobile(soup)
    link_result = await _check_links(soup, url)
    sitemap_result = await _check_sitemap_robots(url)
    perf_result = _check_performance(page["load_time"], html, page.get("headers", {}))
    security_result = _check_security(page.get("final_url", url), page.get("headers", {}))

    # Calculate total
    total = (meta_result["score"] + heading_result["score"] + image_result["score"] +
             mobile_result["score"] + link_result["score"] + sitemap_result["score"] +
             perf_result["score"] + security_result["score"])

    max_total = 100

    # Collect all issues
    all_issues = []
    for cat_name, result in [
        ("Meta Tags", meta_result), ("Headings", heading_result),
        ("Hình ảnh", image_result), ("Mobile", mobile_result),
        ("Links", link_result), ("Sitemap/Robots", sitemap_result),
        ("Performance", perf_result), ("Bảo mật", security_result),
    ]:
        for issue in result.get("issues", []):
            issue["category"] = cat_name
            all_issues.append(issue)

    # Sort: critical first
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    all_issues.sort(key=lambda x: severity_order.get(x.get("severity", "info"), 3))

    # Grade
    if total >= 85: grade, label = "A", "Xuất sắc"
    elif total >= 70: grade, label = "B", "Tốt"
    elif total >= 50: grade, label = "C", "Trung bình"
    elif total >= 30: grade, label = "D", "Cần cải thiện"
    else: grade, label = "F", "Yếu"

    return {
        "url": url,
        "final_url": page.get("final_url", url),
        "score": total,
        "max_score": max_total,
        "grade": grade,
        "grade_label": label,
        "load_time": page["load_time"],
        "redirects": page.get("redirects", 0),
        "breakdown": {
            "meta_tags": {"score": meta_result["score"], "max": meta_result["max"], "details": meta_result},
            "headings": {"score": heading_result["score"], "max": heading_result["max"], "details": heading_result},
            "images": {"score": image_result["score"], "max": image_result["max"], "details": image_result},
            "mobile": {"score": mobile_result["score"], "max": mobile_result["max"], "details": mobile_result},
            "links": {"score": link_result["score"], "max": link_result["max"], "details": link_result},
            "sitemap_robots": {"score": sitemap_result["score"], "max": sitemap_result["max"], "details": sitemap_result},
            "performance": {"score": perf_result["score"], "max": perf_result["max"], "details": perf_result},
            "security": {"score": security_result["score"], "max": security_result["max"], "details": security_result},
        },
        "issues": all_issues,
        "total_issues": len(all_issues),
        "critical_count": sum(1 for i in all_issues if i["severity"] == "critical"),
        "warning_count": sum(1 for i in all_issues if i["severity"] == "warning"),
    }
