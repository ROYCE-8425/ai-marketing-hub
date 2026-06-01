"""
API Advisor Router — Phase 21

Provides:
- POST /api/advisor/analyze — Consolidates site SEO/marketing data, runs deterministic diagnosis, and generates AI advice.
"""

from __future__ import annotations

import os
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from core.auth import get_current_user

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


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/advisor/analyze
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/analyze")
async def analyze_site_api(body: SiteAdvisorRequest, user: dict = Depends(get_current_user)):
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
        include_usage_history=body.include_usage_history
    )
    
    return result
