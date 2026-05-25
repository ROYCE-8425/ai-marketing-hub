"""
HTML Page Parser — DOM-based feature extraction.

Parses real HTML into structured PageFeatures.
All values are MEASURED FACTS from the DOM — no scoring, no heuristic.
This module is the single source of truth for live page analysis.
"""

import re
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


@dataclass
class PageFeatures:
    """All measured facts from DOM — no scoring, no heuristic."""

    # ── Page identity ─────────────────────────────────────────────────────
    url: str = ""
    page_type: str = "other"  # homepage | article | product | service | listing | other
    page_type_confidence: str = "low"  # high | medium | low

    # ── Metadata (measured from <head>) ───────────────────────────────────
    meta_title: str = ""
    meta_title_length: int = 0
    meta_description: str = ""
    meta_description_length: int = 0
    canonical_url: Optional[str] = None
    has_noindex: bool = False
    lang_attribute: str = ""
    og_tags: Dict[str, str] = field(default_factory=dict)

    # ── Headings (measured from DOM) ──────────────────────────────────────
    h1_texts: List[str] = field(default_factory=list)
    h2_texts: List[str] = field(default_factory=list)
    h3_texts: List[str] = field(default_factory=list)
    h1_count: int = 0
    h2_count: int = 0
    h3_count: int = 0

    # ── Links (measured from <a> tags) ────────────────────────────────────
    internal_links: int = 0
    external_links: int = 0
    nofollow_links: int = 0
    broken_anchors: int = 0  # href="#" or empty

    # ── Content (measured from visible text) ──────────────────────────────
    visible_text: str = ""
    word_count: int = 0
    paragraph_count: int = 0
    avg_paragraph_words: float = 0.0
    has_lists: bool = False
    list_count: int = 0
    has_tables: bool = False
    table_count: int = 0

    # ── Media (measured from DOM) ─────────────────────────────────────────
    images_total: int = 0
    images_with_alt: int = 0
    images_missing_alt: int = 0
    has_video: bool = False
    has_lazy_loading: bool = False

    # ── Structured data (measured from <script type="application/ld+json">)
    schema_types: List[str] = field(default_factory=list)
    schema_objects: List[Dict[str, Any]] = field(default_factory=list)
    schema_count: int = 0

    # ── Technical signals (measured) ──────────────────────────────────────
    has_viewport: bool = False
    is_https: bool = False


def parse_html_page(html: str, url: str = "") -> PageFeatures:
    """
    Parse raw HTML into structured PageFeatures.

    All values are MEASURED from the DOM.
    The only heuristic is page_type detection, which is clearly labeled
    with a confidence level.

    Args:
        html: Raw HTML string
        url: Original URL (for link classification)

    Returns:
        PageFeatures dataclass with all measured facts
    """
    soup = BeautifulSoup(html, "lxml")
    features = PageFeatures(url=url)

    # ── Technical signals ─────────────────────────────────────────────────
    features.is_https = url.startswith("https")
    html_tag = soup.find("html")
    features.lang_attribute = html_tag.get("lang", "") if html_tag else ""

    # ── Metadata ──────────────────────────────────────────────────────────
    _extract_metadata(soup, features)

    # ── Headings ──────────────────────────────────────────────────────────
    _extract_headings(soup, features)

    # ── Links ─────────────────────────────────────────────────────────────
    _extract_links(soup, features, url)

    # ── Content ───────────────────────────────────────────────────────────
    _extract_content(soup, features)

    # ── Media ─────────────────────────────────────────────────────────────
    _extract_media(soup, features)

    # ── Structured data ───────────────────────────────────────────────────
    _extract_schemas(soup, features)

    # ── Page type detection (heuristic — labeled) ─────────────────────────
    _detect_page_type(features, url)

    return features


# ─── Extraction helpers ──────────────────────────────────────────────────────


def _extract_metadata(soup: BeautifulSoup, f: PageFeatures) -> None:
    """Extract meta tags from <head>."""
    # Title
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        f.meta_title = title_tag.string.strip()
        f.meta_title_length = len(f.meta_title)

    # Meta description
    desc_tag = soup.find("meta", attrs={"name": "description"})
    if desc_tag:
        f.meta_description = desc_tag.get("content", "").strip()
        f.meta_description_length = len(f.meta_description)

    # Canonical
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    if canonical_tag:
        f.canonical_url = canonical_tag.get("href", "")

    # Noindex
    robots_meta = soup.find("meta", attrs={"name": "robots"})
    if robots_meta:
        content = robots_meta.get("content", "").lower()
        f.has_noindex = "noindex" in content

    # Viewport
    viewport = soup.find("meta", attrs={"name": "viewport"})
    f.has_viewport = viewport is not None and "width=device-width" in (viewport.get("content", ""))

    # Open Graph
    for prop in ["og:title", "og:description", "og:image", "og:type", "og:url"]:
        tag = soup.find("meta", attrs={"property": prop})
        if tag and tag.get("content"):
            f.og_tags[prop] = tag["content"]


def _extract_headings(soup: BeautifulSoup, f: PageFeatures) -> None:
    """Extract headings from DOM."""
    for h1 in soup.find_all("h1"):
        text = h1.get_text(strip=True)
        if text:
            f.h1_texts.append(text)
    f.h1_count = len(f.h1_texts)

    for h2 in soup.find_all("h2"):
        text = h2.get_text(strip=True)
        if text:
            f.h2_texts.append(text)
    f.h2_count = len(f.h2_texts)

    for h3 in soup.find_all("h3"):
        text = h3.get_text(strip=True)
        if text:
            f.h3_texts.append(text)
    f.h3_count = len(f.h3_texts)


def _extract_links(soup: BeautifulSoup, f: PageFeatures, base_url: str) -> None:
    """Extract and classify links from <a> tags."""
    domain = urlparse(base_url).netloc if base_url else ""
    internal = 0
    external = 0
    nofollow = 0
    broken = 0

    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()

        # Skip non-link anchors
        if not href or href.startswith("javascript:") or href.startswith("tel:") or href.startswith("mailto:"):
            continue

        if href == "#" or href == "":
            broken += 1
            continue

        # Classify
        full_url = urljoin(base_url, href) if base_url else href
        link_domain = urlparse(full_url).netloc

        if domain and link_domain == domain:
            internal += 1
        elif href.startswith("http"):
            external += 1
        elif href.startswith("/") or href.startswith("./"):
            internal += 1
        else:
            # Relative URL, count as internal
            internal += 1

        # Nofollow
        rel = a.get("rel", [])
        if isinstance(rel, list) and "nofollow" in rel:
            nofollow += 1
        elif isinstance(rel, str) and "nofollow" in rel:
            nofollow += 1

    f.internal_links = internal
    f.external_links = external
    f.nofollow_links = nofollow
    f.broken_anchors = broken


def _extract_content(soup: BeautifulSoup, f: PageFeatures) -> None:
    """Extract visible text content, stripping nav/footer/script noise."""
    # Clone soup to avoid modifying original
    content_soup = BeautifulSoup(str(soup), "lxml")

    # Remove noise tags
    for tag in content_soup(["nav", "script", "style", "footer", "header", "noscript", "aside"]):
        tag.decompose()

    # Get visible text
    text = content_soup.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    f.visible_text = text

    # Word count
    words = text.split()
    f.word_count = len(words)

    # Paragraphs
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip() and len(p.split()) > 3]
    f.paragraph_count = len(paragraphs)
    if paragraphs:
        f.avg_paragraph_words = sum(len(p.split()) for p in paragraphs) / len(paragraphs)

    # Lists
    ul_tags = soup.find_all("ul")
    ol_tags = soup.find_all("ol")
    f.list_count = len(ul_tags) + len(ol_tags)
    f.has_lists = f.list_count > 0

    # Tables
    tables = soup.find_all("table")
    f.table_count = len(tables)
    f.has_tables = f.table_count > 0


def _extract_media(soup: BeautifulSoup, f: PageFeatures) -> None:
    """Extract image and video data from DOM."""
    images = soup.find_all("img")
    f.images_total = len(images)
    f.images_with_alt = sum(1 for img in images if img.get("alt", "").strip())
    f.images_missing_alt = f.images_total - f.images_with_alt

    # Lazy loading
    f.has_lazy_loading = any(img.get("loading") == "lazy" for img in images)

    # Video
    videos = soup.find_all(["video", "iframe"])
    youtube = any("youtube" in str(v.get("src", "")) for v in videos)
    f.has_video = len(videos) > 0 or youtube


def _extract_schemas(soup: BeautifulSoup, f: PageFeatures) -> None:
    """Extract JSON-LD schema data."""
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict):
                    schema_type = item.get("@type", "Unknown")
                    f.schema_types.append(schema_type)
                    f.schema_objects.append(item)
        except (json.JSONDecodeError, AttributeError):
            pass
    f.schema_count = len(f.schema_types)


def _detect_page_type(f: PageFeatures, url: str) -> None:
    """
    Detect page type from URL pattern + content signals.

    This is the ONLY heuristic in this module.
    Confidence is explicitly labeled.
    """
    path = urlparse(url).path.rstrip("/").lower() if url else ""

    # ── High-confidence detections ────────────────────────────────────────

    # Schema-based (highest confidence)
    if "Product" in f.schema_types:
        f.page_type = "product"
        f.page_type_confidence = "high"
        return
    if "Article" in f.schema_types or "BlogPosting" in f.schema_types or "NewsArticle" in f.schema_types:
        f.page_type = "article"
        f.page_type_confidence = "high"
        return

    # ── Medium-confidence detections ──────────────────────────────────────

    # Homepage
    if path in ("", "/", "/index.html", "/home"):
        f.page_type = "homepage"
        f.page_type_confidence = "high"
        return

    # URL patterns
    article_patterns = ["/blog/", "/bai-viet/", "/tin-tuc/", "/news/", "/article/", "/post/"]
    product_patterns = ["/san-pham/", "/product/", "/shop/", "/sp/"]
    service_patterns = ["/dich-vu/", "/service/", "/solution/"]
    listing_patterns = ["/danh-muc/", "/category/", "/collection/", "/tag/"]

    for pat in article_patterns:
        if pat in path:
            f.page_type = "article"
            f.page_type_confidence = "medium"
            return

    for pat in product_patterns:
        if pat in path:
            f.page_type = "product"
            f.page_type_confidence = "medium"
            return

    for pat in service_patterns:
        if pat in path:
            f.page_type = "service"
            f.page_type_confidence = "medium"
            return

    for pat in listing_patterns:
        if pat in path:
            f.page_type = "listing"
            f.page_type_confidence = "medium"
            return

    # ── Low-confidence heuristic ──────────────────────────────────────────
    # Content-based: long article-like content
    if f.word_count > 1500 and f.h2_count >= 3:
        f.page_type = "article"
        f.page_type_confidence = "low"
        return

    if f.word_count < 500 and f.h2_count <= 2:
        f.page_type = "service"
        f.page_type_confidence = "low"
        return

    f.page_type = "other"
    f.page_type_confidence = "low"
