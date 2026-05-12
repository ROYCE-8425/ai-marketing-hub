"""
Satellite API Router — GEO Satellite Pipeline

Endpoints for managing satellite site network:
- CRUD satellite sites
- Spin content + auto-post to satellites
- Bulk posting
- Post history + index status
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter

router = APIRouter(prefix="/api/satellite", tags=["Satellite Sites"])


# ── Request Models ───────────────────────────────────────────────────────────


class AddSiteRequest(BaseModel):
    name: str = Field(..., description="Tên site vệ tinh")
    url: str = Field(..., description="URL site")
    platform: str = Field("blogger", description="Platform: blogger | wordpress | custom")
    blog_id: str = Field("", description="Blogger Blog ID (nếu platform=blogger)")
    api_key: str = Field("", description="API key (tuỳ chọn)")
    wp_username: str = Field("", description="WordPress username")
    wp_app_password: str = Field("", description="WordPress App Password")


class SpinAndPostRequest(BaseModel):
    content: str = Field(..., description="Nội dung gốc cần spin")
    title: str = Field("", description="Tiêu đề bài viết")
    site_ids: List[str] = Field(default_factory=list, description="ID các site muốn đăng (rỗng = tất cả)")
    spin_level: str = Field("medium", description="Mức spin: light | medium | heavy")
    spin_tone: str = Field("neutral", description="Giọng văn: professional | friendly | sales | neutral")
    backlink_url: str = Field("", description="URL cần backlink (main site)")
    backlink_keyword: str = Field("", description="Từ khóa cho anchor text")
    preserve_keywords: Optional[List[str]] = Field(None, description="Từ khóa SEO cần giữ nguyên")
    labels: Optional[List[str]] = Field(None, description="Labels/tags cho bài viết")
    num_versions: int = Field(1, description="Số bản spin (1 bản/site)")


class PostDirectRequest(BaseModel):
    site_id: str = Field(..., description="ID site để đăng")
    title: str = Field(..., description="Tiêu đề bài")
    content_html: str = Field(..., description="Nội dung HTML")
    backlink_url: str = Field("", description="URL backlink")
    backlink_keyword: str = Field("", description="Keyword backlink")
    labels: Optional[List[str]] = None


class CheckIndexRequest(BaseModel):
    url: str = Field(..., description="URL cần kiểm tra index")


# ── Endpoints ────────────────────────────────────────────────────────────────


@router.get("/sites")
async def list_sites():
    """Lấy danh sách tất cả satellite sites."""
    from core.satellite_manager import get_satellite_sites
    return {"sites": get_satellite_sites()}


@router.post("/sites")
async def add_site(body: AddSiteRequest):
    """Thêm satellite site mới (Blogger/WordPress)."""
    from core.satellite_manager import add_satellite_site
    site = add_satellite_site(
        name=body.name,
        url=body.url,
        platform=body.platform,
        blog_id=body.blog_id,
        api_key=body.api_key,
        wp_username=body.wp_username,
        wp_app_password=body.wp_app_password,
    )
    return {"status": "ok", "site": site}


@router.delete("/sites/{site_id}")
async def remove_site(site_id: str):
    """Xóa satellite site."""
    from core.satellite_manager import delete_satellite_site
    delete_satellite_site(site_id)
    return {"status": "deleted", "site_id": site_id}


@router.get("/posts")
async def list_posts(limit: int = 50):
    """Lấy lịch sử bài đã đăng."""
    from core.satellite_manager import get_satellite_posts
    posts = get_satellite_posts(limit=limit)
    return {"posts": posts, "total": len(posts)}


@router.post("/post-direct")
async def post_direct(body: PostDirectRequest):
    """Đăng bài trực tiếp lên satellite site (không spin)."""
    from core.satellite_manager import post_to_satellite
    result = await post_to_satellite(
        site_id=body.site_id,
        title=body.title,
        content_html=body.content_html,
        labels=body.labels,
        backlink_url=body.backlink_url,
        backlink_keyword=body.backlink_keyword,
    )
    return result


@router.post("/spin-and-post")
async def spin_and_post(body: SpinAndPostRequest):
    """Spin nội dung bằng AI rồi tự động đăng lên satellite sites."""
    from core.satellite_manager import get_satellite_sites, post_to_satellite
    from core.spin_editor import spin_for_satellite

    # 1. Get target sites
    all_sites = get_satellite_sites()
    if body.site_ids:
        target_sites = [s for s in all_sites if s["id"] in body.site_ids]
    else:
        target_sites = [s for s in all_sites if s.get("status") == "active"]

    if not target_sites:
        return {"error": "Không có satellite site nào để đăng. Thêm site trước."}

    # 2. Spin content for each site
    spin_result = await spin_for_satellite(
        content=body.content,
        num_versions=len(target_sites),
        level=body.spin_level,
        tone=body.spin_tone,
        preserve_keywords=body.preserve_keywords,
        backlink_url=body.backlink_url,
        backlink_keyword=body.backlink_keyword,
    )

    if spin_result.get("error"):
        return spin_result

    versions = spin_result.get("versions", [])
    if not versions:
        return {"error": "Không tạo được nội dung spin"}

    # 3. Post each version to a different site
    results = []
    for i, site in enumerate(target_sites):
        version = versions[i % len(versions)]
        title = body.title or f"Bài viết - {site['name']}"

        # Vary title slightly per site
        if i > 0 and body.title:
            title = f"{body.title} | {site['name']}"

        post_result = await post_to_satellite(
            site_id=site["id"],
            title=title,
            content_html=version["content_html"],
            labels=body.labels,
            backlink_url=body.backlink_url,
            backlink_keyword=body.backlink_keyword,
        )
        results.append({
            "site": site["name"],
            "site_id": site["id"],
            "uniqueness": version.get("uniqueness_percent", 0),
            **post_result,
        })

    success_count = sum(1 for r in results if r.get("success"))
    return {
        "total_sites": len(target_sites),
        "success": success_count,
        "failed": len(target_sites) - success_count,
        "results": results,
    }


@router.post("/check-index")
async def check_index(body: CheckIndexRequest):
    """Kiểm tra URL đã được Google index chưa."""
    from core.satellite_manager import check_index_status
    return await check_index_status(body.url)
