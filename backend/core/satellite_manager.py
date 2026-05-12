"""
Satellite Site Manager — GEO Satellite Pipeline

Manages satellite blog network for backlink building:
- CRUD for satellite sites (Blogger, WordPress, custom)
- Auto-post spun content to Blogger via Blogger API v3
- Auto-post to WordPress via REST API
- Backlink injection with diverse anchor texts
- Index status checking via Google
"""

import os
import json
import uuid
import random
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

import httpx

# ── Storage ──────────────────────────────────────────────────────────────────
DB_DIR = Path(__file__).parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
SITES_FILE = DB_DIR / "satellite_sites.json"
POSTS_FILE = DB_DIR / "satellite_posts.json"

# ── Helpers ──────────────────────────────────────────────────────────────────


def _load_json(path: Path) -> List[Dict]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_json(path: Path, data: List[Dict]):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Site CRUD ────────────────────────────────────────────────────────────────


def get_satellite_sites() -> List[Dict]:
    """Get all satellite sites."""
    return _load_json(SITES_FILE)


def add_satellite_site(
    name: str,
    url: str,
    platform: str = "blogger",
    blog_id: str = "",
    api_key: str = "",
    wp_username: str = "",
    wp_app_password: str = "",
) -> Dict[str, Any]:
    """Add a new satellite site."""
    sites = _load_json(SITES_FILE)
    site = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "url": url.rstrip("/"),
        "platform": platform,  # blogger | wordpress | custom
        "blog_id": blog_id,
        "api_key": api_key,
        "wp_username": wp_username,
        "wp_app_password": wp_app_password,
        "total_posts": 0,
        "created_at": datetime.now().isoformat(),
        "status": "active",
    }
    sites.append(site)
    _save_json(SITES_FILE, sites)
    return site


def delete_satellite_site(site_id: str) -> bool:
    """Delete a satellite site."""
    sites = _load_json(SITES_FILE)
    sites = [s for s in sites if s["id"] != site_id]
    _save_json(SITES_FILE, sites)
    return True


def update_satellite_site(site_id: str, updates: Dict) -> Optional[Dict]:
    """Update a satellite site."""
    sites = _load_json(SITES_FILE)
    for site in sites:
        if site["id"] == site_id:
            site.update(updates)
            _save_json(SITES_FILE, sites)
            return site
    return None


# ── Post History ─────────────────────────────────────────────────────────────


def get_satellite_posts(limit: int = 50) -> List[Dict]:
    """Get posted content history."""
    posts = _load_json(POSTS_FILE)
    posts.sort(key=lambda p: p.get("posted_at", ""), reverse=True)
    return posts[:limit]


def _save_post_record(record: Dict):
    """Save a post record."""
    posts = _load_json(POSTS_FILE)
    posts.append(record)
    _save_json(POSTS_FILE, posts)

    # Update site post count
    sites = _load_json(SITES_FILE)
    for site in sites:
        if site["id"] == record.get("site_id"):
            site["total_posts"] = site.get("total_posts", 0) + 1
    _save_json(SITES_FILE, sites)


# ── Backlink Injection ───────────────────────────────────────────────────────

ANCHOR_TEMPLATES = [
    "xem thêm tại {keyword}",
    "{keyword} - chi tiết",
    "tham khảo: {keyword}",
    "{keyword}",
    "đọc thêm về {keyword}",
    "tìm hiểu {keyword} tại đây",
    "{keyword} uy tín",
    "nguồn: {keyword}",
]


def inject_backlink(
    content: str,
    target_url: str,
    keyword: str,
    position: str = "end",  # start | middle | end | random
) -> str:
    """Inject a backlink into content with natural anchor text."""
    template = random.choice(ANCHOR_TEMPLATES)
    anchor_text = template.format(keyword=keyword)
    link_html = f'<a href="{target_url}" target="_blank" rel="noopener">{anchor_text}</a>'

    paragraphs = content.split("\n\n")
    if not paragraphs:
        return content + f"\n\n{link_html}"

    if position == "start" and len(paragraphs) > 1:
        paragraphs[1] = paragraphs[1] + f" {link_html}"
    elif position == "middle":
        mid = len(paragraphs) // 2
        paragraphs[mid] = paragraphs[mid] + f" {link_html}"
    elif position == "random":
        idx = random.randint(0, len(paragraphs) - 1)
        paragraphs[idx] = paragraphs[idx] + f" {link_html}"
    else:  # end
        paragraphs[-1] = paragraphs[-1] + f"\n\n{link_html}"

    return "\n\n".join(paragraphs)


# ── Blogger API v3 ───────────────────────────────────────────────────────────


async def _get_blogger_access_token() -> Optional[str]:
    """Reuse GSC OAuth2 credentials to get access token for Blogger API."""
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"), override=True)

    client_id = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
    secret = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET", "")
    refresh = os.getenv("GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN", "")

    if not all([client_id, secret, refresh]):
        return None

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post("https://oauth2.googleapis.com/token", data={
                "client_id": client_id,
                "client_secret": secret,
                "refresh_token": refresh,
                "grant_type": "refresh_token",
            })
            return resp.json().get("access_token")
    except Exception:
        return None


async def post_to_blogger(
    blog_id: str,
    title: str,
    content_html: str,
    labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Post content to Blogger via API v3."""
    token = await _get_blogger_access_token()
    if not token:
        return {"error": "Không lấy được access token. Kiểm tra OAuth credentials."}

    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"

    body: Dict[str, Any] = {
        "kind": "blogger#post",
        "title": title,
        "content": content_html,
    }
    if labels:
        body["labels"] = labels

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=body,
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                return {
                    "success": True,
                    "post_id": data.get("id"),
                    "post_url": data.get("url"),
                    "title": data.get("title"),
                    "published": data.get("published"),
                }
            else:
                return {"error": f"Blogger API error {resp.status_code}: {resp.text[:300]}"}
    except Exception as e:
        return {"error": f"Blogger post failed: {str(e)}"}


# ── WordPress REST API ───────────────────────────────────────────────────────


async def post_to_wordpress(
    wp_url: str,
    wp_username: str,
    wp_app_password: str,
    title: str,
    content_html: str,
    categories: Optional[List[int]] = None,
    tags: Optional[List[int]] = None,
    status: str = "publish",
) -> Dict[str, Any]:
    """Post content to WordPress via REST API."""
    endpoint = f"{wp_url.rstrip('/')}/wp-json/wp/v2/posts"

    body: Dict[str, Any] = {
        "title": title,
        "content": content_html,
        "status": status,
    }
    if categories:
        body["categories"] = categories
    if tags:
        body["tags"] = tags

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                endpoint,
                auth=(wp_username, wp_app_password),
                json=body,
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                return {
                    "success": True,
                    "post_id": data.get("id"),
                    "post_url": data.get("link"),
                    "title": data.get("title", {}).get("rendered", title),
                    "published": data.get("date"),
                }
            else:
                return {"error": f"WordPress API error {resp.status_code}: {resp.text[:300]}"}
    except Exception as e:
        return {"error": f"WordPress post failed: {str(e)}"}


# ── Unified Post Function ────────────────────────────────────────────────────


async def post_to_satellite(
    site_id: str,
    title: str,
    content_html: str,
    labels: Optional[List[str]] = None,
    backlink_url: str = "",
    backlink_keyword: str = "",
) -> Dict[str, Any]:
    """Post content to a satellite site (auto-detect platform)."""
    sites = _load_json(SITES_FILE)
    site = next((s for s in sites if s["id"] == site_id), None)
    if not site:
        return {"error": f"Site {site_id} không tồn tại"}

    # Inject backlink if requested
    final_content = content_html
    if backlink_url and backlink_keyword:
        final_content = inject_backlink(
            content_html, backlink_url, backlink_keyword,
            position=random.choice(["middle", "end"]),
        )

    platform = site.get("platform", "blogger")
    if platform == "blogger":
        result = await post_to_blogger(
            blog_id=site["blog_id"],
            title=title,
            content_html=final_content,
            labels=labels,
        )
    elif platform == "wordpress":
        result = await post_to_wordpress(
            wp_url=site["url"],
            wp_username=site.get("wp_username", ""),
            wp_app_password=site.get("wp_app_password", ""),
            title=title,
            content_html=final_content,
        )
    else:
        return {"error": f"Platform '{platform}' chưa được hỗ trợ"}

    # Save post record
    record = {
        "id": str(uuid.uuid4())[:8],
        "site_id": site_id,
        "site_name": site["name"],
        "platform": platform,
        "title": title,
        "post_url": result.get("post_url", ""),
        "post_id": result.get("post_id", ""),
        "backlink_url": backlink_url,
        "backlink_keyword": backlink_keyword,
        "status": "published" if result.get("success") else "failed",
        "error": result.get("error", ""),
        "posted_at": datetime.now().isoformat(),
        "indexed": False,
    }
    _save_post_record(record)

    return {**result, "record": record}


# ── Index Check ──────────────────────────────────────────────────────────────


async def check_index_status(url: str) -> Dict[str, Any]:
    """Check if a URL is indexed by Google (via site: query)."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://www.google.com/search",
                params={"q": f"site:{url}"},
                headers={"User-Agent": "Mozilla/5.0"},
            )
            indexed = "did not match any documents" not in resp.text
            return {"url": url, "indexed": indexed}
    except Exception:
        return {"url": url, "indexed": False, "error": "Check failed"}
