"""
API Advisor Router — Phase 21

Provides:
- POST /api/advisor/analyze — Consolidates site SEO/marketing data, runs deterministic diagnosis, and generates AI advice.
"""

from __future__ import annotations

import os
from typing import Optional, Literal
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field
from core.auth import get_current_user

from sqlalchemy.orm import Session
from core.database import get_db

router = APIRouter(prefix="/api/advisor", tags=["Phase 21 — AI Website Advisor"])


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response Schemas
# ─────────────────────────────────────────────────────────────────────────────

class SiteAdvisorRequest(BaseModel):
    site_url: Optional[str] = Field(None, description="Đường dẫn trang web cần phân tích (tùy chọn)")
    target_keyword: Optional[str] = Field(None, description="Từ khóa mục tiêu (bắt buộc cho phân tích SERP)")
    days: int = Field(30, description="Khoảng thời gian phân tích (mặc định 30 ngày)")
    
    include_gsc: bool = Field(True, description="Bao gồm dữ liệu Google Search Console")
    include_ga4: bool = Field(True, description="Bao gồm dữ liệu Google Analytics 4")
    include_serp: bool = Field(True, description="Bao gồm dữ liệu SERP trực tiếp")
    include_rank_tracking: bool = Field(True, description="Bao gồm thứ hạng từ khóa theo dõi")
    include_technical: bool = Field(True, description="Bao gồm kiểm tra kỹ thuật Technical SEO")
    include_cwv: bool = Field(True, description="Bao gồm kiểm tra tốc độ Core Web Vitals")
    include_schema: bool = Field(True, description="Bao gồm xác thực Schema.org JSON-LD")
    include_usage_history: bool = Field(True, description="Bao gồm lịch sử sử dụng hệ thống")


class AdvisorExportRequest(BaseModel):
    format: Literal["json", "markdown", "html"] = "markdown"
    advisor_result: dict



# ─────────────────────────────────────────────────────────────────────────────
# POST /api/advisor/analyze
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/analyze")
async def analyze_site_api(
    body: SiteAdvisorRequest, 
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phân tích toàn diện và đưa ra đề xuất cố vấn tối ưu hóa website.
    Gom dữ liệu từ GSC, GA4, Technical SEO, v.v., tính deterministic insights,
    sau đó dùng AI để tổng hợp Tóm tắt & Kế hoạch hành động 7 ngày / 30 ngày.
    """
    # Lazy import to ensure server starts instantly without performance overhead
    from core.site_advisor import analyze_site

    result = await analyze_site(
        site_url=body.site_url,
        target_keyword=body.target_keyword,
        days=body.days,
        include_gsc=body.include_gsc,
        include_ga4=body.include_ga4,
        include_serp=body.include_serp,
        include_rank_tracking=body.include_rank_tracking,
        include_technical=body.include_technical,
        include_cwv=body.include_cwv,
        include_schema=body.include_schema,
        include_usage_history=body.include_usage_history,
        db=db
    )
    
    return result


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/advisor/export
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/export")
async def export_advisor_report_api(
    body: AdvisorExportRequest,
    user: dict = Depends(get_current_user)
):
    """
    Xuất kết quả chẩn đoán SEO AI thành các định dạng JSON, Markdown, hoặc HTML.
    Nhận dữ liệu chẩn đoán hiện tại từ client, lọc và kiểm tra bảo mật, sau đó kết xuất file.
    """
    # Lazy imports for performance
    from core.advisor_report_generator import (
        build_exportable_advisor_report,
        export_report_as_json,
        export_report_as_markdown,
        export_report_as_html,
    )
    import re
    from urllib.parse import urlparse
    from datetime import datetime

    # 1. Sanitize & build safe report structure
    clean_data = build_exportable_advisor_report(body.advisor_result)

    # 2. Determine file extension and media type
    fmt = body.format.lower()
    if fmt == "json":
        content = export_report_as_json(clean_data)
        media_type = "application/json"
        ext = "json"
    elif fmt == "html":
        content = export_report_as_html(clean_data)
        media_type = "text/html"
        ext = "html"
    else:
        # fallback to markdown
        content = export_report_as_markdown(clean_data)
        media_type = "text/markdown"
        ext = "md"

    # 3. Sanitize site_url to form a secure filename
    site_url = clean_data.get("site_url") or "site"
    try:
        parsed = urlparse(site_url)
        netloc = parsed.netloc or parsed.path
        netloc = netloc.split(":")[0]  # remove port
        sanitized_site = re.sub(r'[^a-zA-Z0-9\-]', '-', netloc)
        sanitized_site = re.sub(r'-+', '-', sanitized_site).strip('-')
        if not sanitized_site:
            sanitized_site = "site"
    except Exception:
        sanitized_site = "site"

    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"advisor-report-{sanitized_site}-{current_date}.{ext}"

    # 4. Return file response
    return Response(
        content=content.encode("utf-8"),
        media_type=f"{media_type}; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        }
    )

