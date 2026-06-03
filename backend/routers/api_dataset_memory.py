"""
SEO Dataset Memory API Router — Phase 22

Provides query and read endpoints for keyword memories and recommendation outcomes,
fully authenticated and protected against cross-site data leakage.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.auth import get_current_user
from core.database import get_db

router = APIRouter(prefix="/api/dataset", tags=["Phase 22 — SEO Dataset Memory"])


def serialize_keyword_memory(item) -> Dict[str, Any]:
    """Helper to convert SEOKeywordMemory SQLAlchemy model to a clean dictionary."""
    evidence = {}
    if item.evidence_json:
        try:
            evidence = json.loads(item.evidence_json)
        except Exception:
            evidence = {"raw": item.evidence_json}
            
    return {
        "id": item.id,
        "site_id": item.site_id,
        "advisor_run_id": item.advisor_run_id,
        "site_url": item.site_url,
        "keyword": item.keyword,
        "normalized_keyword": item.normalized_keyword,
        "page_url": item.page_url,
        "page_type": item.page_type,
        "search_intent": item.search_intent,
        "source": item.source,
        "clicks": item.clicks,
        "impressions": item.impressions,
        "ctr": item.ctr,
        "avg_position": item.avg_position,
        "trend_direction": item.trend_direction,
        "opportunity_type": item.opportunity_type,
        "confidence_score": item.confidence_score,
        "evidence_json": evidence,
        "observed_at": item.observed_at.isoformat() if item.observed_at else None,
        "created_at": item.created_at.isoformat() if item.created_at else None
    }


def serialize_recommendation_outcome(item) -> Dict[str, Any]:
    """Helper to convert SEORecommendationOutcome SQLAlchemy model to a clean dictionary."""
    measured_delta = {}
    if item.measured_delta_json:
        try:
            measured_delta = json.loads(item.measured_delta_json)
        except Exception:
            measured_delta = {"raw": item.measured_delta_json}
            
    return {
        "id": item.id,
        "site_id": item.site_id,
        "advisor_run_id": item.advisor_run_id,
        "recommendation_type": item.recommendation_type,
        "recommendation_text": item.recommendation_text,
        "priority": item.priority,
        "impact": item.impact,
        "page_url": item.page_url,
        "keyword": item.keyword,
        "status": item.status,
        "outcome": item.outcome,
        "execution_note": item.execution_note,
        "measured_delta_json": measured_delta,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. KEYWORD MEMORY ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/keywords")
async def get_keywords_api(
    site_url: Optional[str] = Query(None, description="URL trang web lọc kết quả"),
    opportunity_type: Optional[str] = Query(None, description="Loại cơ hội: quick_wins, ctr_opportunity, rank_drops, v.v."),
    source: Optional[str] = Query(None, description="Nguồn dữ liệu: gsc, manual, v.v."),
    days: Optional[int] = Query(None, description="Số ngày gần đây lọc dữ liệu"),
    sort_by: str = Query("newest", description="Sắp xếp theo: newest, impressions, opportunity_type"),
    limit: int = Query(100, ge=1, le=1000, description="Số dòng giới hạn tối đa"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Truy vấn lịch sử cơ hội từ khóa (SEO Keyword Memory) của website,
    hỗ trợ lọc theo loại, nguồn dữ liệu, thời gian và sắp xếp linh hoạt.
    """
    # Lazy import to speed up server startup times
    from core.seo_intelligence import get_keyword_memory

    records, total = get_keyword_memory(
        db=db,
        site_url=site_url,
        opportunity_type=opportunity_type,
        source=source,
        limit=limit,
        days=days,
        sort_by=sort_by
    )
    serialized = [serialize_keyword_memory(r) for r in records]
    return {
        "site_url": site_url,
        "total": total,
        "items": serialized
    }


@router.get("/keywords/summary")
async def get_keywords_summary_api(
    site_url: Optional[str] = Query(None, description="URL trang web lọc kết quả"),
    days: Optional[int] = Query(None, description="Số ngày gần đây lọc dữ liệu"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy thống kê tổng hợp của SEO Keyword Memory:
    - Tổng số cơ hội từ khóa
    - Phân rã theo loại cơ hội (opportunity_type)
    - Top 10 từ khóa có lượt hiển thị (impressions) cao nhất
    """
    # Lazy import to speed up server startup times
    from core.seo_intelligence import get_keyword_memory_summary

    summary = get_keyword_memory_summary(db=db, site_url=site_url, days=days)
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# 2. RECOMMENDATION OUTCOME ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/recommendations")
async def get_recommendations_api(
    site_url: Optional[str] = Query(None, description="URL trang web lọc kết quả"),
    status: Optional[str] = Query(None, description="Trạng thái thực thi: pending, in_progress, completed, failed"),
    advisor_run_id: Optional[int] = Query(None, description="ID của lượt chạy Advisor"),
    recommendation_type: Optional[str] = Query(None, description="Loại đề xuất tối ưu"),
    limit: int = Query(100, ge=1, le=1000, description="Số dòng giới hạn tối đa"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Truy vấn lịch sử thực thi các khuyến nghị (SEO Recommendation Outcomes) của website,
    hỗ trợ lọc theo trạng thái, ID lượt chạy Advisor và loại đề xuất.
    """
    # Lazy import to speed up server startup times
    from core.seo_intelligence import get_recommendation_outcomes

    records, total = get_recommendation_outcomes(
        db=db,
        site_url=site_url,
        status=status,
        advisor_run_id=advisor_run_id,
        recommendation_type=recommendation_type,
        limit=limit
    )
    serialized = [serialize_recommendation_outcome(r) for r in records]
    return {
        "site_url": site_url,
        "total": total,
        "items": serialized
    }


@router.get("/recommendations/summary")
async def get_recommendations_summary_api(
    site_url: Optional[str] = Query(None, description="URL trang web lọc kết quả"),
    advisor_run_id: Optional[int] = Query(None, description="ID của lượt chạy Advisor"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy thống kê tổng hợp về kết quả thực thi khuyến nghị:
    - Tổng số khuyến nghị
    - Số lượng theo các trạng thái (pending, in_progress, completed, failed)
    - Số lượng theo loại khuyến nghị
    - Số lượng theo mức độ ưu tiên (priority)
    """
    # Lazy import to speed up server startup times
    from core.seo_intelligence import get_recommendation_outcomes_summary

    summary = get_recommendation_outcomes_summary(db=db, site_url=site_url, advisor_run_id=advisor_run_id)
    return summary


def serialize_pattern_memory(item) -> Dict[str, Any]:
    """Helper to convert SEOPatternMemory SQLAlchemy model to a clean dictionary."""
    payload = {}
    if item.pattern_payload_json:
        try:
            payload = json.loads(item.pattern_payload_json)
        except Exception:
            payload = {"raw": item.pattern_payload_json}
            
    return {
        "id": item.id,
        "site_id": item.site_id,
        "advisor_run_id": item.advisor_run_id,
        "pattern_type": item.pattern_type,
        "pattern_label": item.pattern_label,
        "page_type": item.page_type,
        "search_intent": item.search_intent,
        "source": item.source,
        "confidence_score": item.confidence_score,
        "outcome_score": item.outcome_score,
        "pattern_payload_json": payload,
        "observed_at": item.observed_at.isoformat() if item.observed_at else None,
        "created_at": item.created_at.isoformat() if item.created_at else None
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. SEO PATTERN MEMORY ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/patterns")
async def get_patterns_api(
    site_url: Optional[str] = Query(None, description="URL trang web lọc kết quả"),
    pattern_type: Optional[str] = Query(None, description="Loại pattern cần lọc"),
    page_type: Optional[str] = Query(None, description="Loại trang lọc: home, service, article, category"),
    search_intent: Optional[str] = Query(None, description="Ý định tìm kiếm: commercial, informational, transactional"),
    source: Optional[str] = Query(None, description="Nguồn gốc phát hiện pattern"),
    days: Optional[int] = Query(None, description="Số ngày gần đây lọc dữ liệu"),
    limit: int = Query(100, ge=1, le=1000, description="Số dòng giới hạn tối đa"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Truy vấn lịch sử các mẫu SEO (SEO Pattern Memory) đã ghi nhận trên website,
    hỗ trợ lọc theo loại, nguồn phát hiện, thời gian và các chiều trang/ý định tìm kiếm.
    """
    from core.seo_intelligence import get_pattern_memory

    records, total = get_pattern_memory(
        db=db,
        site_url=site_url,
        pattern_type=pattern_type,
        page_type=page_type,
        search_intent=search_intent,
        source=source,
        days=days,
        limit=limit
    )
    serialized = [serialize_pattern_memory(r) for r in records]
    return {
        "site_url": site_url,
        "total": total,
        "items": serialized
    }


@router.get("/patterns/summary")
async def get_patterns_summary_api(
    site_url: Optional[str] = Query(None, description="URL trang web lọc kết quả"),
    days: Optional[int] = Query(None, description="Số ngày gần đây lọc dữ liệu"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy thống kê tổng hợp của SEO Pattern Memory:
    - Tổng số pattern ghi nhận
    - Phân bố theo loại mẫu (pattern_type)
    - Phân bố theo loại trang (page_type)
    - Danh sách các mẫu lặp lại nhiều nhất
    """
    from core.seo_intelligence import get_pattern_memory_summary

    summary = get_pattern_memory_summary(db=db, site_url=site_url, days=days)
    return summary


class RecommendationOutcomeUpdate(BaseModel):
    status: str = Field(..., description="Trạng thái thực thi: pending, in_progress, completed, failed")
    outcome: Optional[str] = Field(None, description="Kết quả thực tế sau khi áp dụng")
    measured_delta_json: Optional[Dict[str, Any]] = Field(None, description="Số liệu chênh lệch KPI đo lường được")
    execution_note: Optional[str] = Field(None, description="Ghi chú quá trình thực thi")


@router.put("/recommendations/{id}")
async def update_recommendation_outcome_api(
    id: int,
    body: RecommendationOutcomeUpdate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cập nhật trạng thái thực thi và kết quả đo lường (KPI Delta, Note) của một khuyến nghị theo ID.
    """
    from core.seo_intelligence import update_recommendation_outcome
    
    try:
        updated_item = update_recommendation_outcome(
            db=db,
            outcome_id=id,
            status=body.status,
            outcome=body.outcome,
            measured_delta_json=body.measured_delta_json,
            execution_note=body.execution_note
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khuyến nghị với ID {id}."
        )
        
    return serialize_recommendation_outcome(updated_item)
