"""
SEO Intelligence Data Layer Ingestion Service — Phase 22

Provides ingestion, normalization, and derived calculations for GSC, GA4,
and technical audits, caching results cleanly across SQLite and PostgreSQL.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from sqlalchemy import func
from sqlalchemy.orm import Session
from core.models import (
    ManagedSite,
    SEORawSnapshot,
    SEONormalizedPage,
    SEONormalizedIssue,
    SEOAdvisorRun,
    SEODerivedSignal,
    SEORecommendationMemory,
    SEOKeywordMemory,
    SEORecommendationOutcome,
    SEOPatternMemory
)


def normalize_site_domain(url: str) -> str:
    """Normalize a site URL/domain to a standard format for strict matching."""
    if not url:
        return ""
    u = url.strip().lower()
    # Remove protocol
    if u.startswith("https://"):
        u = u[8:]
    elif u.startswith("http://"):
        u = u[7:]
    # Remove www.
    if u.startswith("www."):
        u = u[4:]
    # Remove trailing slashes and paths
    domain = u.split("/")[0]
    return domain


def _get_or_create_site(db: Session, site_url: str) -> ManagedSite:
    """Helper to fetch a managed site instance by its exact or normalized domain or create one."""
    target_norm = normalize_site_domain(site_url)
    
    # Query all sites and find exact normalized domain match strictly
    all_sites = db.query(ManagedSite).all()
    site = None
    for s in all_sites:
        if normalize_site_domain(s.url) == target_norm:
            site = s
            break
                
    if not site:
        # Fallback owner (usually default admin user ID 1)
        from core.models import User
        admin = db.query(User).filter(User.role == "admin").first()
        admin_id = admin.id if admin else 1
        
        # Ensure we use a clean site URL with scheme
        clean_url = site_url.strip()
        if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
            clean_url = f"https://{clean_url}"
            
        site = ManagedSite(
            user_id=admin_id,
            name=target_norm,
            url=clean_url,
            description="Auto-generated site for intelligence ingestion",
            is_active=True
        )
        db.add(site)
        db.commit()
        db.refresh(site)
        
    return site


# ═══════════════════════════════════════════════════════════════
# 1. RAW SNAPSHOT INGESTION
# ═══════════════════════════════════════════════════════════════

def ingest_raw_snapshot(db: Session, site_url: str, source: str, raw_data: Any) -> SEORawSnapshot:
    """Store raw provider JSON data dump cleanly in the database."""
    site = _get_or_create_site(db, site_url)
    
    # Convert data payload to JSON string safely
    try:
        raw_json = json.dumps(raw_data, ensure_ascii=False)
    except Exception:
        raw_json = str(raw_data)
        
    snapshot = SEORawSnapshot(
        site_id=site.id,
        source=source,
        raw_data=raw_json
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


# ═══════════════════════════════════════════════════════════════
# 2. NORMALIZATION HELPERS
# ═══════════════════════════════════════════════════════════════

def normalize_site_page(
    db: Session, 
    site_url: str, 
    page_url: str, 
    title: Optional[str] = None, 
    meta_description: Optional[str] = None
) -> SEONormalizedPage:
    """Upsert a normalized crawled page with metadata to track history."""
    site = _get_or_create_site(db, site_url)
    
    # Check if page already exists for this site
    normalized_page = db.query(SEONormalizedPage).filter(
        SEONormalizedPage.site_id == site.id,
        SEONormalizedPage.url == page_url
    ).first()
    
    if normalized_page:
        if title is not None:
            normalized_page.title = title
        if meta_description is not None:
            normalized_page.meta_description = meta_description
        normalized_page.updated_at = datetime.now()
    else:
        normalized_page = SEONormalizedPage(
            site_id=site.id,
            url=page_url,
            title=title or "",
            meta_description=meta_description or ""
        )
        db.add(normalized_page)
        
    db.commit()
    db.refresh(normalized_page)
    return normalized_page


def ingest_normalized_issue(
    db: Session,
    site_url: str,
    page_url: Optional[str],
    category: str,
    severity: str,
    message: str,
    fix_action: Optional[str] = None
) -> SEONormalizedIssue:
    """Record a unique SEO technical issue or warning if not already active."""
    site = _get_or_create_site(db, site_url)
    
    # Check if this exact issue is already recorded and unresolved
    existing_issue = db.query(SEONormalizedIssue).filter(
        SEONormalizedIssue.site_id == site.id,
        SEONormalizedIssue.page_url == page_url,
        SEONormalizedIssue.category == category,
        SEONormalizedIssue.message == message,
        SEONormalizedIssue.is_resolved == False
    ).first()
    
    if existing_issue:
        # Update details or severity
        existing_issue.severity = severity
        if fix_action:
            existing_issue.fix_action = fix_action
        db.commit()
        db.refresh(existing_issue)
        return existing_issue
        
    # Create new issue
    new_issue = SEONormalizedIssue(
        site_id=site.id,
        page_url=page_url,
        category=category,
        severity=severity,
        message=message,
        fix_action=fix_action,
        is_resolved=False
    )
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)
    return new_issue


def ingest_advisor_run(
    db: Session,
    site_url: str,
    days: int,
    target_keyword: Optional[str],
    result: Dict[str, Any]
) -> SEOAdvisorRun:
    """Ingest a full unified AI Advisor execution history."""
    site = _get_or_create_site(db, site_url)
    
    # Parse plan items securely
    action_7d_json = json.dumps(result.get("action_plan_7d", []), ensure_ascii=False)
    action_30d_json = json.dumps(result.get("action_plan_30d", []), ensure_ascii=False)
    
    run = SEOAdvisorRun(
        site_id=site.id,
        days=days,
        target_keyword=target_keyword,
        confidence_score=float(result.get("confidence_score", 100.0)),
        summary=result.get("summary", ""),
        action_plan_7d=action_7d_json,
        action_plan_30d=action_30d_json,
        ai_provider=result.get("ai_provider", "builtin_template")
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


# ═══════════════════════════════════════════════════════════════
# 3. DERIVED SIGNALS INGESTION
# ═══════════════════════════════════════════════════════════════

def ingest_derived_signal(
    db: Session,
    site_url: str,
    signal_type: str,
    entity_identifier: str,
    signal_data: Dict[str, Any],
    advisor_run_id: Optional[int] = None
) -> SEODerivedSignal:
    """Upsert calculated intelligence signals (quick wins, rank drops, etc.). Keeps history over advisor runs."""
    site = _get_or_create_site(db, site_url)
    
    # Check if this signal for this entity already exists for the given advisor run (or within 5 minutes if no run is provided)
    if advisor_run_id:
        existing = db.query(SEODerivedSignal).filter(
            SEODerivedSignal.site_id == site.id,
            SEODerivedSignal.signal_type == signal_type,
            SEODerivedSignal.entity_identifier == entity_identifier,
            SEODerivedSignal.advisor_run_id == advisor_run_id
        ).first()
    else:
        # Prevent duplication in short interval if run not passed
        time_limit = datetime.now() - timedelta(minutes=5)
        existing = db.query(SEODerivedSignal).filter(
            SEODerivedSignal.site_id == site.id,
            SEODerivedSignal.signal_type == signal_type,
            SEODerivedSignal.entity_identifier == entity_identifier,
            SEODerivedSignal.calculated_at >= time_limit
        ).order_by(SEODerivedSignal.calculated_at.desc()).first()
    
    try:
        data_json = json.dumps(signal_data, ensure_ascii=False)
    except Exception:
        data_json = str(signal_data)
        
    if existing:
        existing.signal_data = data_json
        existing.calculated_at = datetime.now()
        if advisor_run_id:
            existing.advisor_run_id = advisor_run_id
        db.commit()
        db.refresh(existing)
        return existing
        
    # Create new signal record
    new_signal = SEODerivedSignal(
        site_id=site.id,
        advisor_run_id=advisor_run_id,
        signal_type=signal_type,
        entity_identifier=entity_identifier,
        signal_data=data_json
    )
    db.add(new_signal)
    db.commit()
    db.refresh(new_signal)
    return new_signal


# ═══════════════════════════════════════════════════════════════
# 4. RECOMMENDATION OUTCOME TRACKER
# ═══════════════════════════════════════════════════════════════

def record_recommendation_memory(
    db: Session,
    site_url: str,
    rule_name: str,
    recommendation_text: str,
    outcome: str = "pending",
    feedback: Optional[str] = None
) -> SEORecommendationMemory:
    """Track recommendations offered to the user and accumulate optimization outcomes. Prevents duplicates if active."""
    site = _get_or_create_site(db, site_url)
    
    # Avoid duplicate pending/active recommendations with the exact same text for the site
    existing = db.query(SEORecommendationMemory).filter(
        SEORecommendationMemory.site_id == site.id,
        SEORecommendationMemory.rule_name == rule_name,
        SEORecommendationMemory.recommendation_text == recommendation_text,
        SEORecommendationMemory.outcome == outcome
    ).first()
    
    if existing:
        if feedback is not None:
            existing.feedback = feedback
        db.commit()
        db.refresh(existing)
        return existing
        
    rec = SEORecommendationMemory(
        site_id=site.id,
        rule_name=rule_name,
        recommendation_text=recommendation_text,
        outcome=outcome,
        feedback=feedback
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def record_keyword_memory(
    db: Session,
    site_url: str,
    keyword: str,
    source: str,
    opportunity_type: str,
    clicks: int,
    impressions: int,
    ctr: float,
    avg_position: float,
    advisor_run_id: Optional[int] = None,
    page_url: Optional[str] = None,
    page_type: Optional[str] = None,
    search_intent: Optional[str] = None,
    trend_direction: Optional[str] = None,
    confidence_score: float = 100.0,
    evidence_json: Optional[Dict[str, Any]] = None,
    observed_at: Optional[datetime] = None
) -> SEOKeywordMemory:
    """
    Record keyword memory with metadata.
    De-duplicates observations of the same keyword, site and opportunity type:
    - If metrics are identical to a record from the last 24 hours, or if it falls
      within a 5-minute cooldown, updates that record instead of duplicating.
    - Otherwise, inserts a new record to preserve historical trend progression.
    """
    site = _get_or_create_site(db, site_url)
    norm_kw = " ".join(keyword.lower().strip().split())
    
    # Save evidence safely as a JSON string
    evidence_str = "{}"
    if evidence_json:
        try:
            evidence_str = json.dumps(evidence_json, ensure_ascii=False)
        except Exception:
            evidence_str = str(evidence_json)
            
    if not observed_at:
        observed_at = datetime.now()

    # Query the most recent entry within 24 hours
    time_limit = observed_at - timedelta(hours=24)
    existing = db.query(SEOKeywordMemory).filter(
        SEOKeywordMemory.site_id == site.id,
        SEOKeywordMemory.normalized_keyword == norm_kw,
        SEOKeywordMemory.opportunity_type == opportunity_type,
        SEOKeywordMemory.observed_at >= time_limit
    ).order_by(SEOKeywordMemory.observed_at.desc()).first()
    
    if existing:
        is_identical = (
            existing.clicks == clicks and
            existing.impressions == impressions and
            abs(existing.ctr - ctr) < 0.01 and
            abs(existing.avg_position - avg_position) < 0.1
        )
        is_recent_cooldown = (observed_at - existing.observed_at) <= timedelta(minutes=5)
        
        if is_identical or is_recent_cooldown:
            existing.clicks = clicks
            existing.impressions = impressions
            existing.ctr = ctr
            existing.avg_position = avg_position
            existing.page_url = page_url
            existing.page_type = page_type
            existing.search_intent = search_intent
            existing.trend_direction = trend_direction
            existing.confidence_score = confidence_score
            existing.evidence_json = evidence_str
            existing.observed_at = observed_at
            if advisor_run_id is not None:
                existing.advisor_run_id = advisor_run_id
            db.commit()
            db.refresh(existing)
            return existing
        
    new_mem = SEOKeywordMemory(
        site_id=site.id,
        advisor_run_id=advisor_run_id,
        site_url=site.url,
        keyword=keyword,
        normalized_keyword=norm_kw,
        page_url=page_url,
        page_type=page_type,
        search_intent=search_intent,
        source=source,
        clicks=clicks,
        impressions=impressions,
        ctr=ctr,
        avg_position=avg_position,
        trend_direction=trend_direction,
        opportunity_type=opportunity_type,
        confidence_score=confidence_score,
        evidence_json=evidence_str,
        observed_at=observed_at
    )
    db.add(new_mem)
    db.commit()
    db.refresh(new_mem)
    return new_mem


def record_recommendation_outcome(
    db: Session,
    site_url: str,
    recommendation_type: str,
    recommendation_text: str,
    advisor_run_id: Optional[int] = None,
    priority: Optional[str] = None,
    impact: Optional[str] = None,
    page_url: Optional[str] = None,
    keyword: Optional[str] = None,
    status: str = "pending"
) -> SEORecommendationOutcome:
    """
    Record recommendation outcome seed from advisor.
    This tracks the execution instances of advisor advice.
    """
    site = _get_or_create_site(db, site_url)
    
    # Avoid recording duplicate recommendation text with pending status for the same run
    existing = db.query(SEORecommendationOutcome).filter(
        SEORecommendationOutcome.site_id == site.id,
        SEORecommendationOutcome.advisor_run_id == advisor_run_id,
        SEORecommendationOutcome.recommendation_type == recommendation_type,
        SEORecommendationOutcome.recommendation_text == recommendation_text,
        SEORecommendationOutcome.status == status
    ).first()
    
    if existing:
        existing.page_url = page_url
        existing.keyword = keyword
        existing.priority = priority
        existing.impact = impact
        db.commit()
        db.refresh(existing)
        return existing
        
    rec_outcome = SEORecommendationOutcome(
        site_id=site.id,
        advisor_run_id=advisor_run_id,
        recommendation_type=recommendation_type,
        recommendation_text=recommendation_text,
        priority=priority,
        impact=impact,
        page_url=page_url,
        keyword=keyword,
        status=status
    )
    db.add(rec_outcome)
    db.commit()
    db.refresh(rec_outcome)
    return rec_outcome


def get_keyword_memory(
    db: Session,
    site_url: Optional[str] = None,
    opportunity_type: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 100,
    days: Optional[int] = None,
    sort_by: str = "newest"
) -> Tuple[List[SEOKeywordMemory], int]:
    """Retrieve filtered and sorted SEO keyword memory records along with total matching count."""
    query = db.query(SEOKeywordMemory)
    
    if site_url:
        # Resolve target domain strictly to prevent cross-site leaks
        target_norm = normalize_site_domain(site_url)
        # Find exact site match
        all_sites = db.query(ManagedSite).all()
        matched_site = None
        for s in all_sites:
            if normalize_site_domain(s.url) == target_norm:
                matched_site = s
                break
        if matched_site:
            query = query.filter(SEOKeywordMemory.site_id == matched_site.id)
        else:
            return [], 0
            
    if opportunity_type:
        query = query.filter(SEOKeywordMemory.opportunity_type == opportunity_type)
        
    if source:
        query = query.filter(SEOKeywordMemory.source == source)
        
    if days is not None:
        time_limit = datetime.now() - timedelta(days=days)
        query = query.filter(SEOKeywordMemory.observed_at >= time_limit)
        
    # Get total matching count before limit
    total_count = query.count()
        
    # Apply sorting
    if sort_by == "impressions":
        query = query.order_by(SEOKeywordMemory.impressions.desc())
    elif sort_by == "opportunity_type":
        query = query.order_by(SEOKeywordMemory.opportunity_type.asc(), SEOKeywordMemory.observed_at.desc())
    else:  # newest
        query = query.order_by(SEOKeywordMemory.observed_at.desc())
        
    return query.limit(limit).all(), total_count


def get_keyword_memory_summary(
    db: Session,
    site_url: Optional[str] = None,
    days: Optional[int] = None
) -> Dict[str, Any]:
    """Generate aggregate statistics and summary metrics for keyword memory."""
    site_id = None
    if site_url:
        target_norm = normalize_site_domain(site_url)
        all_sites = db.query(ManagedSite).all()
        for s in all_sites:
            if normalize_site_domain(s.url) == target_norm:
                site_id = s.id
                break
        if not site_id:
            return {
                "total": 0,
                "by_opportunity_type": {},
                "top_keywords": []
            }
            
    base_query = db.query(SEOKeywordMemory)
    if site_id:
        base_query = base_query.filter(SEOKeywordMemory.site_id == site_id)
    if days is not None:
        time_limit = datetime.now() - timedelta(days=days)
        base_query = base_query.filter(SEOKeywordMemory.observed_at >= time_limit)
        
    total = base_query.count()
    
    # Group by opportunity type
    by_type = {}
    type_counts = base_query.with_entities(
        SEOKeywordMemory.opportunity_type, func.count(SEOKeywordMemory.id)
    ).group_by(SEOKeywordMemory.opportunity_type).all()
    for opp_type, count in type_counts:
        by_type[opp_type] = count
        
    # Top keywords by impressions
    top_items = base_query.order_by(SEOKeywordMemory.impressions.desc()).limit(10).all()
    top_keywords = []
    for item in top_items:
        top_keywords.append({
            "keyword": item.keyword,
            "clicks": item.clicks,
            "impressions": item.impressions,
            "ctr": item.ctr,
            "avg_position": item.avg_position,
            "opportunity_type": item.opportunity_type
        })
        
    return {
        "total": total,
        "by_opportunity_type": by_type,
        "top_keywords": top_keywords
    }


def get_recommendation_outcomes(
    db: Session,
    site_url: Optional[str] = None,
    status: Optional[str] = None,
    advisor_run_id: Optional[int] = None,
    recommendation_type: Optional[str] = None,
    limit: int = 100
) -> Tuple[List[SEORecommendationOutcome], int]:
    """Retrieve filtered SEO recommendation outcomes (run execution instances) along with total matching count."""
    query = db.query(SEORecommendationOutcome)
    
    if site_url:
        target_norm = normalize_site_domain(site_url)
        all_sites = db.query(ManagedSite).all()
        matched_site = None
        for s in all_sites:
            if normalize_site_domain(s.url) == target_norm:
                matched_site = s
                break
        if matched_site:
            query = query.filter(SEORecommendationOutcome.site_id == matched_site.id)
        else:
            return [], 0
            
    if status:
        query = query.filter(SEORecommendationOutcome.status == status)
        
    if advisor_run_id is not None:
        query = query.filter(SEORecommendationOutcome.advisor_run_id == advisor_run_id)
        
    if recommendation_type:
        query = query.filter(SEORecommendationOutcome.recommendation_type == recommendation_type)
        
    # Get total matching count before limit
    total_count = query.count()
        
    # Show newest first
    query = query.order_by(SEORecommendationOutcome.created_at.desc())
    
    return query.limit(limit).all(), total_count


def get_recommendation_outcomes_summary(
    db: Session,
    site_url: Optional[str] = None,
    advisor_run_id: Optional[int] = None
) -> Dict[str, Any]:
    """Generate aggregate statistics and summary metrics for recommendation outcomes."""
    site_id = None
    if site_url:
        target_norm = normalize_site_domain(site_url)
        all_sites = db.query(ManagedSite).all()
        for s in all_sites:
            if normalize_site_domain(s.url) == target_norm:
                site_id = s.id
                break
        if not site_id:
            return {
                "total": 0,
                "pending": 0,
                "in_progress": 0,
                "completed": 0,
                "failed": 0,
                "completed_with_delta_count": 0,
                "by_type": {},
                "by_priority": {}
            }
            
    base_query = db.query(SEORecommendationOutcome)
    if site_id:
        base_query = base_query.filter(SEORecommendationOutcome.site_id == site_id)
    if advisor_run_id is not None:
        base_query = base_query.filter(SEORecommendationOutcome.advisor_run_id == advisor_run_id)
        
    total = base_query.count()
    
    # Status breakdown
    pending = base_query.filter(SEORecommendationOutcome.status == "pending").count()
    in_progress = base_query.filter(SEORecommendationOutcome.status == "in_progress").count()
    completed = base_query.filter(SEORecommendationOutcome.status == "completed").count()
    failed = base_query.filter(SEORecommendationOutcome.status == "failed").count()
    
    # Count completed outcomes with deltas
    completed_with_delta_count = base_query.filter(
        SEORecommendationOutcome.status == "completed",
        SEORecommendationOutcome.measured_delta_json.isnot(None),
        SEORecommendationOutcome.measured_delta_json != "",
        SEORecommendationOutcome.measured_delta_json != "{}"
    ).count()
    
    # Group by recommendation type
    by_type = {}
    type_counts = base_query.with_entities(
        SEORecommendationOutcome.recommendation_type, func.count(SEORecommendationOutcome.id)
    ).group_by(SEORecommendationOutcome.recommendation_type).all()
    for rec_type, count in type_counts:
        by_type[rec_type] = count
        
    # Group by priority
    by_priority = {}
    priority_counts = base_query.with_entities(
        SEORecommendationOutcome.priority, func.count(SEORecommendationOutcome.id)
    ).group_by(SEORecommendationOutcome.priority).all()
    for prio, count in priority_counts:
        prio_key = prio if prio else "undefined"
        by_priority[prio_key] = count
        
    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "failed": failed,
        "completed_with_delta_count": completed_with_delta_count,
        "by_type": by_type,
        "by_priority": by_priority
    }


def update_recommendation_outcome(
    db: Session,
    outcome_id: int,
    status: str,
    outcome: Optional[str] = None,
    measured_delta_json: Optional[Dict[str, Any]] = None,
    execution_note: Optional[str] = None
) -> Optional[SEORecommendationOutcome]:
    """
    Update status, execution note, final outcome and KPI deltas of a recommendation.
    Validates status strictly against: pending, in_progress, completed, failed.
    Sets reviewed_at ONLY when transitioning to completed or failed.
    """
    allowed_statuses = {"pending", "in_progress", "completed", "failed"}
    if status not in allowed_statuses:
        raise ValueError(f"Trạng thái '{status}' không hợp lệ. Trạng thái phải là một trong: {', '.join(allowed_statuses)}")

    rec_outcome = db.query(SEORecommendationOutcome).filter(SEORecommendationOutcome.id == outcome_id).first()
    if not rec_outcome:
        return None

    rec_outcome.status = status
    
    if execution_note is not None:
        rec_outcome.execution_note = execution_note
        
    if outcome is not None:
        rec_outcome.outcome = outcome

    if measured_delta_json is not None:
        try:
            rec_outcome.measured_delta_json = json.dumps(measured_delta_json, ensure_ascii=False)
        except Exception:
            rec_outcome.measured_delta_json = str(measured_delta_json)

    # updated_at is always updated
    rec_outcome.updated_at = datetime.now()

    # reviewed_at is ONLY set when transitioning to completed or failed
    if status in ("completed", "failed"):
        rec_outcome.reviewed_at = datetime.now()

    db.commit()
    db.refresh(rec_outcome)
    return rec_outcome


def build_keyword_memory_context(db: Session, site_url: str) -> Dict[str, Any]:
    """
    Builds a summary of keyword memory for the AI advisor.
    Identifies recurring opportunities, recent queries, and performance trends.
    """
    target_norm = normalize_site_domain(site_url)
    all_sites = db.query(ManagedSite).all()
    site = None
    for s in all_sites:
        if normalize_site_domain(s.url) == target_norm:
            site = s
            break
            
    if not site:
        return {
            "total_keyword_records": 0,
            "top_recurring_keywords": [],
            "recurring_quick_wins": [],
            "recurring_low_ctr_opportunities": [],
            "recent_keywords": []
        }
        
    # Total records count
    total_records = db.query(SEOKeywordMemory).filter(SEOKeywordMemory.site_id == site.id).count()
    
    # Recurring keywords (any opportunity type)
    recurring_kw_rows = db.query(
        SEOKeywordMemory.keyword,
        SEOKeywordMemory.opportunity_type,
        func.count(SEOKeywordMemory.id).label("cnt"),
        func.max(SEOKeywordMemory.impressions).label("max_impressions"),
        func.max(SEOKeywordMemory.clicks).label("max_clicks"),
        func.max(SEOKeywordMemory.ctr).label("max_ctr")
    ).filter(
        SEOKeywordMemory.site_id == site.id
    ).group_by(
        SEOKeywordMemory.keyword,
        SEOKeywordMemory.opportunity_type
    ).order_by(
        func.count(SEOKeywordMemory.id).desc()
    ).limit(30).all()
    
    top_recurring = []
    recurring_quick_wins = []
    recurring_low_ctr = []
    
    for row in recurring_kw_rows:
        item = {
            "keyword": row.keyword,
            "opportunity_type": row.opportunity_type,
            "occurrences": row.cnt,
            "impressions": row.max_impressions,
            "clicks": row.max_clicks,
            "ctr": row.max_ctr
        }
        if row.cnt > 1:
            top_recurring.append(item)
            if row.opportunity_type in ("quick_win", "quick_wins"):
                recurring_quick_wins.append(item)
            elif row.opportunity_type == "low_ctr_high_impression":
                recurring_low_ctr.append(item)
                
    # Recent keywords (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_records = db.query(SEOKeywordMemory).filter(
        SEOKeywordMemory.site_id == site.id,
        SEOKeywordMemory.observed_at >= seven_days_ago
    ).order_by(
        SEOKeywordMemory.observed_at.desc()
    ).limit(15).all()
    
    recent_keywords = [{
        "keyword": r.keyword,
        "opportunity_type": r.opportunity_type,
        "clicks": r.clicks,
        "impressions": r.impressions,
        "ctr": r.ctr,
        "avg_position": r.avg_position,
        "observed_at": r.observed_at.isoformat() if r.observed_at else None
    } for r in recent_records]
    
    return {
        "total_keyword_records": total_records,
        "top_recurring_keywords": top_recurring[:10],
        "recurring_quick_wins": recurring_quick_wins[:10],
        "recurring_low_ctr_opportunities": recurring_low_ctr[:10],
        "recent_keywords": recent_keywords
    }


def build_recommendation_memory_context(db: Session, site_url: str) -> Dict[str, Any]:
    """
    Builds a summary of past recommendation outcomes for the AI advisor.
    Identifies repeated advisor recommendations and tracks pending tasks.
    """
    target_norm = normalize_site_domain(site_url)
    all_sites = db.query(ManagedSite).all()
    site = None
    for s in all_sites:
        if normalize_site_domain(s.url) == target_norm:
            site = s
            break
            
    if not site:
        return {
            "total_recommendations": 0,
            "pending_recommendations_count": 0,
            "pending_recommendations": [],
            "in_progress_recommendations": [],
            "top_recurring_types": {},
            "repeated_recommendations": []
        }
        
    # Total count
    total_recs = db.query(SEORecommendationOutcome).filter(SEORecommendationOutcome.site_id == site.id).count()
    
    # Pending list
    pending_recs = db.query(SEORecommendationOutcome).filter(
        SEORecommendationOutcome.site_id == site.id,
        SEORecommendationOutcome.status == "pending"
    ).order_by(SEORecommendationOutcome.created_at.desc()).limit(15).all()
    
    pending_list = [{
        "id": r.id,
        "recommendation_type": r.recommendation_type,
        "recommendation_text": r.recommendation_text,
        "priority": r.priority,
        "impact": r.impact,
        "status": r.status,
        "page_url": r.page_url,
        "keyword": r.keyword,
        "created_at": r.created_at.isoformat() if r.created_at else None
    } for r in pending_recs]

    # In progress list
    in_progress_recs = db.query(SEORecommendationOutcome).filter(
        SEORecommendationOutcome.site_id == site.id,
        SEORecommendationOutcome.status == "in_progress"
    ).order_by(SEORecommendationOutcome.created_at.desc()).limit(15).all()
    
    in_progress_list = [{
        "id": r.id,
        "recommendation_type": r.recommendation_type,
        "recommendation_text": r.recommendation_text,
        "priority": r.priority,
        "impact": r.impact,
        "status": r.status,
        "page_url": r.page_url,
        "keyword": r.keyword,
        "created_at": r.created_at.isoformat() if r.created_at else None
    } for r in in_progress_recs]
    
    # Group by recommendation type
    type_counts = db.query(
        SEORecommendationOutcome.recommendation_type,
        func.count(SEORecommendationOutcome.id).label("cnt")
    ).filter(
        SEORecommendationOutcome.site_id == site.id
    ).group_by(SEORecommendationOutcome.recommendation_type).all()
    
    top_types = {t.recommendation_type: t.cnt for t in type_counts}
    
    # Repeated recommendation texts (appeared in > 1 runs)
    repeated_rows = db.query(
        SEORecommendationOutcome.recommendation_text,
        SEORecommendationOutcome.recommendation_type,
        SEORecommendationOutcome.priority,
        func.count(SEORecommendationOutcome.id).label("cnt"),
        func.max(SEORecommendationOutcome.created_at).label("last_seen")
    ).filter(
        SEORecommendationOutcome.site_id == site.id
    ).group_by(
        SEORecommendationOutcome.recommendation_text,
        SEORecommendationOutcome.recommendation_type,
        SEORecommendationOutcome.priority
    ).order_by(
        func.count(SEORecommendationOutcome.id).desc()
    ).limit(20).all()
    
    repeated_list = [{
        "recommendation_text": row.recommendation_text,
        "recommendation_type": row.recommendation_type,
        "priority": row.priority,
        "occurrences": row.cnt,
        "last_seen": row.last_seen.isoformat() if row.last_seen else None
    } for row in repeated_rows if row.cnt > 1]
    
    return {
        "total_recommendations": total_recs,
        "pending_recommendations_count": len(pending_list),
        "pending_recommendations": pending_list,
        "in_progress_recommendations": in_progress_list,
        "top_recurring_types": top_types,
        "repeated_recommendations": repeated_list
    }


def build_outcome_tracking_context(db: Session, site_url: str) -> Dict[str, Any]:
    """
    Builds a summary of recommendation outcome execution history.
    Identifies completed tasks, failed tasks, and delta impacts to feed to the advisor.
    """
    target_norm = normalize_site_domain(site_url)
    all_sites = db.query(ManagedSite).all()
    site = None
    for s in all_sites:
        if normalize_site_domain(s.url) == target_norm:
            site = s
            break

    if not site:
        return {
            "total_outcomes": 0,
            "pending_count": 0,
            "in_progress_count": 0,
            "completed_count": 0,
            "failed_count": 0,
            "completed_with_delta_count": 0,
            "repeated_pending_recommendations": [],
            "successful_recommendation_types": {},
            "failed_recommendation_types": {},
            "recent_completed_recommendations": [],
            "recent_failed_recommendations": []
        }

    # Query all recommendation outcomes for the site
    outcomes = db.query(SEORecommendationOutcome).filter(
        SEORecommendationOutcome.site_id == site.id
    ).all()

    total_outcomes = len(outcomes)
    pending_count = 0
    in_progress_count = 0
    completed_count = 0
    failed_count = 0
    completed_with_delta_count = 0

    successful_recommendation_types = {}
    failed_recommendation_types = {}

    for o in outcomes:
        if o.status == "pending":
            pending_count += 1
        elif o.status == "in_progress":
            in_progress_count += 1
        elif o.status == "completed":
            completed_count += 1
            # Check if measured_delta_json is not null/empty/"{}"
            has_delta = False
            if o.measured_delta_json:
                try:
                    delta_data = json.loads(o.measured_delta_json)
                    if delta_data and isinstance(delta_data, dict) and len(delta_data) > 0:
                        has_delta = True
                except Exception:
                    if o.measured_delta_json.strip() not in ("", "{}"):
                        has_delta = True
            
            if has_delta:
                completed_with_delta_count += 1
                rec_type = o.recommendation_type or "undefined"
                successful_recommendation_types[rec_type] = successful_recommendation_types.get(rec_type, 0) + 1
        elif o.status == "failed":
            failed_count += 1
            rec_type = o.recommendation_type or "undefined"
            failed_recommendation_types[rec_type] = failed_recommendation_types.get(rec_type, 0) + 1

    # Fetch recent completed outcomes (newest first, limit 10)
    completed_rows = db.query(SEORecommendationOutcome).filter(
        SEORecommendationOutcome.site_id == site.id,
        SEORecommendationOutcome.status == "completed"
    ).order_by(SEORecommendationOutcome.updated_at.desc()).limit(10).all()

    recent_completed = []
    for r in completed_rows:
        delta = {}
        if r.measured_delta_json:
            try:
                delta = json.loads(r.measured_delta_json)
            except Exception:
                delta = {"raw": r.measured_delta_json}
        recent_completed.append({
            "recommendation_text": r.recommendation_text,
            "recommendation_type": r.recommendation_type,
            "priority": r.priority,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            "measured_delta": delta
        })

    # Fetch recent failed outcomes (newest first, limit 10)
    failed_rows = db.query(SEORecommendationOutcome).filter(
        SEORecommendationOutcome.site_id == site.id,
        SEORecommendationOutcome.status == "failed"
    ).order_by(SEORecommendationOutcome.updated_at.desc()).limit(10).all()

    recent_failed = []
    for r in failed_rows:
        recent_failed.append({
            "recommendation_text": r.recommendation_text,
            "recommendation_type": r.recommendation_type,
            "priority": r.priority,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            "execution_note": r.execution_note
        })

    # Find repeated pending/in-progress recommendations (appearing > 1 times)
    pending_recs = db.query(SEORecommendationOutcome).filter(
        SEORecommendationOutcome.site_id == site.id,
        SEORecommendationOutcome.status.in_(["pending", "in_progress"])
    ).all()

    pending_counts = {}
    pending_details = {}
    for pr in pending_recs:
        norm_text = " ".join(pr.recommendation_text.lower().strip().split())
        pending_counts[norm_text] = pending_counts.get(norm_text, 0) + 1
        if norm_text not in pending_details or (pr.created_at and pending_details[norm_text].created_at and pr.created_at > pending_details[norm_text].created_at):
            pending_details[norm_text] = pr

    repeated_pending = []
    for norm_text, count in pending_counts.items():
        if count > 1:
            pr = pending_details[norm_text]
            repeated_pending.append({
                "recommendation_text": pr.recommendation_text,
                "recommendation_type": pr.recommendation_type,
                "priority": pr.priority,
                "occurrences": count,
                "last_seen": pr.created_at.isoformat() if pr.created_at else None
            })

    return {
        "total_outcomes": total_outcomes,
        "pending_count": pending_count,
        "in_progress_count": in_progress_count,
        "completed_count": completed_count,
        "failed_count": failed_count,
        "completed_with_delta_count": completed_with_delta_count,
        "repeated_pending_recommendations": repeated_pending,
        "successful_recommendation_types": successful_recommendation_types,
        "failed_recommendation_types": failed_recommendation_types,
        "recent_completed_recommendations": recent_completed,
        "recent_failed_recommendations": recent_failed
    }


def record_pattern_memory(
    db: Session,
    site_url: str,
    pattern_type: str,
    pattern_label: str,
    page_type: Optional[str] = None,
    search_intent: Optional[str] = None,
    source: str = "advisor",
    confidence_score: float = 100.0,
    pattern_payload: Optional[Dict[str, Any]] = None,
    advisor_run_id: Optional[int] = None,
    outcome_score: Optional[float] = None,
    observed_at: Optional[datetime] = None
) -> SEOPatternMemory:
    """
    Record a detected high-value pattern for the site.
    De-duplicates observations of the same site, pattern type, and pattern label
    within a 5-minute cooldown period by updating the last record instead of creating duplicates.
    """
    site = _get_or_create_site(db, site_url)
    
    # Serialize payload cleanly
    payload_str = "{}"
    if pattern_payload:
        try:
            payload_str = json.dumps(pattern_payload, ensure_ascii=False)
        except Exception:
            payload_str = str(pattern_payload)
            
    if not observed_at:
        observed_at = datetime.now()
        
    # Check for duplicate in the last 5 minutes leading up to observed_at
    start_limit = observed_at - timedelta(minutes=5)
    existing = db.query(SEOPatternMemory).filter(
        SEOPatternMemory.site_id == site.id,
        SEOPatternMemory.pattern_type == pattern_type,
        SEOPatternMemory.pattern_label == pattern_label,
        SEOPatternMemory.observed_at >= start_limit,
        SEOPatternMemory.observed_at <= observed_at
    ).order_by(SEOPatternMemory.observed_at.desc()).first()
    
    if existing:
        existing.page_type = page_type
        existing.search_intent = search_intent
        existing.source = source
        existing.confidence_score = confidence_score
        existing.outcome_score = outcome_score
        existing.pattern_payload_json = payload_str
        existing.observed_at = observed_at
        if advisor_run_id is not None:
            existing.advisor_run_id = advisor_run_id
        db.commit()
        db.refresh(existing)
        return existing
        
    new_pattern = SEOPatternMemory(
        site_id=site.id,
        advisor_run_id=advisor_run_id,
        pattern_type=pattern_type,
        pattern_label=pattern_label,
        page_type=page_type,
        search_intent=search_intent,
        source=source,
        confidence_score=confidence_score,
        outcome_score=outcome_score,
        pattern_payload_json=payload_str,
        observed_at=observed_at
    )
    db.add(new_pattern)
    db.commit()
    db.refresh(new_pattern)
    return new_pattern


def get_pattern_memory(
    db: Session,
    site_url: Optional[str] = None,
    pattern_type: Optional[str] = None,
    page_type: Optional[str] = None,
    search_intent: Optional[str] = None,
    source: Optional[str] = None,
    days: Optional[int] = None,
    limit: int = 100
) -> Tuple[List[SEOPatternMemory], int]:
    """Retrieve filtered SEO pattern memory records along with total matching count."""
    query = db.query(SEOPatternMemory)
    
    if site_url:
        target_norm = normalize_site_domain(site_url)
        all_sites = db.query(ManagedSite).all()
        matched_site = None
        for s in all_sites:
            if normalize_site_domain(s.url) == target_norm:
                matched_site = s
                break
        if matched_site:
            query = query.filter(SEOPatternMemory.site_id == matched_site.id)
        else:
            return [], 0
            
    if pattern_type:
        query = query.filter(SEOPatternMemory.pattern_type == pattern_type)
        
    if page_type:
        query = query.filter(SEOPatternMemory.page_type == page_type)
        
    if search_intent:
        query = query.filter(SEOPatternMemory.search_intent == search_intent)
        
    if source:
        query = query.filter(SEOPatternMemory.source == source)
        
    if days is not None:
        time_limit = datetime.now() - timedelta(days=days)
        query = query.filter(SEOPatternMemory.observed_at >= time_limit)
        
    total_count = query.count()
    
    # Newest first
    query = query.order_by(SEOPatternMemory.observed_at.desc())
    
    return query.limit(limit).all(), total_count


def get_pattern_memory_summary(
    db: Session,
    site_url: Optional[str] = None,
    days: Optional[int] = None
) -> Dict[str, Any]:
    """Generate aggregate statistics and summary metrics for pattern memory."""
    site_id = None
    if site_url:
        target_norm = normalize_site_domain(site_url)
        all_sites = db.query(ManagedSite).all()
        for s in all_sites:
            if normalize_site_domain(s.url) == target_norm:
                site_id = s.id
                break
        if not site_id:
            return {
                "total": 0,
                "by_pattern_type": {},
                "by_page_type": {},
                "top_patterns": []
            }
            
    base_query = db.query(SEOPatternMemory)
    if site_id:
        base_query = base_query.filter(SEOPatternMemory.site_id == site_id)
    if days is not None:
        time_limit = datetime.now() - timedelta(days=days)
        base_query = base_query.filter(SEOPatternMemory.observed_at >= time_limit)
        
    total = base_query.count()
    
    # Group by pattern type
    by_type = {}
    type_counts = base_query.with_entities(
        SEOPatternMemory.pattern_type, func.count(SEOPatternMemory.id)
    ).group_by(SEOPatternMemory.pattern_type).all()
    for p_type, count in type_counts:
        by_type[p_type] = count
        
    # Group by page type
    by_page = {}
    page_counts = base_query.with_entities(
        SEOPatternMemory.page_type, func.count(SEOPatternMemory.id)
    ).group_by(SEOPatternMemory.page_type).all()
    for pg_type, count in page_counts:
        pg_key = pg_type if pg_type else "undefined"
        by_page[pg_key] = count
        
    # Top patterns by frequency count of pattern labels
    label_counts = base_query.with_entities(
        SEOPatternMemory.pattern_label, 
        SEOPatternMemory.pattern_type,
        func.count(SEOPatternMemory.id).label("cnt")
    ).group_by(
        SEOPatternMemory.pattern_label,
        SEOPatternMemory.pattern_type
    ).order_by(
        func.count(SEOPatternMemory.id).desc()
    ).limit(10).all()
    
    top_patterns = []
    for row in label_counts:
        top_patterns.append({
            "pattern_label": row.pattern_label,
            "pattern_type": row.pattern_type,
            "occurrences": row.cnt
        })
        
    return {
        "total": total,
        "by_pattern_type": by_type,
        "by_page_type": by_page,
        "top_patterns": top_patterns
    }


def build_pattern_memory_context(db: Session, site_url: str) -> Dict[str, Any]:
    """
    Builds a summary of pattern memory for the AI advisor.
    Identifies recurring structural patterns and compiled metrics.
    """
    target_norm = normalize_site_domain(site_url)
    all_sites = db.query(ManagedSite).all()
    site = None
    for s in all_sites:
        if normalize_site_domain(s.url) == target_norm:
            site = s
            break
            
    if not site:
        return {
            "total_patterns": 0,
            "by_pattern_type": {},
            "top_pattern_labels": [],
            "recurring_patterns": [],
            "recent_patterns": [],
            "critical_structural_patterns": [],
            "unresolved_recommendation_patterns": []
        }
        
    # Count total patterns
    total_patterns = db.query(SEOPatternMemory).filter(SEOPatternMemory.site_id == site.id).count()
    
    # Group counts by pattern type
    type_counts = db.query(
        SEOPatternMemory.pattern_type,
        func.count(SEOPatternMemory.id).label("cnt")
    ).filter(
        SEOPatternMemory.site_id == site.id
    ).group_by(SEOPatternMemory.pattern_type).all()
    by_pattern_type = {t.pattern_type: t.cnt for t in type_counts}
    
    # Top pattern labels
    label_counts = db.query(
        SEOPatternMemory.pattern_label,
        func.count(SEOPatternMemory.id).label("cnt")
    ).filter(
        SEOPatternMemory.site_id == site.id
    ).group_by(SEOPatternMemory.pattern_label).order_by(func.count(SEOPatternMemory.id).desc()).limit(10).all()
    
    top_pattern_labels = [{"label": l.pattern_label, "count": l.cnt} for l in label_counts]
    
    # Recent patterns (last 10 records)
    recent_records = db.query(SEOPatternMemory).filter(
        SEOPatternMemory.site_id == site.id
    ).order_by(SEOPatternMemory.observed_at.desc()).limit(10).all()
    
    recent_patterns = []
    for r in recent_records:
        payload = {}
        if r.pattern_payload_json:
            try:
                payload = json.loads(r.pattern_payload_json)
            except Exception:
                payload = {"raw": r.pattern_payload_json}
        recent_patterns.append({
            "id": r.id,
            "pattern_type": r.pattern_type,
            "pattern_label": r.pattern_label,
            "observed_at": r.observed_at.isoformat() if r.observed_at else None,
            "confidence_score": r.confidence_score,
            "pattern_payload": payload
        })
        
    # Recurring pattern labels (occurrences > 1 across runs/records)
    recurring_rows = db.query(
        SEOPatternMemory.pattern_label,
        SEOPatternMemory.pattern_type,
        func.count(SEOPatternMemory.id).label("cnt")
    ).filter(
        SEOPatternMemory.site_id == site.id
    ).group_by(
        SEOPatternMemory.pattern_label,
        SEOPatternMemory.pattern_type
    ).order_by(func.count(SEOPatternMemory.id).desc()).all()
    
    recurring_patterns = []
    critical_structural_patterns = []
    unresolved_recommendation_patterns = []
    
    for row in recurring_rows:
        item = {
            "label": row.pattern_label,
            "type": row.pattern_type,
            "occurrences": row.cnt
        }
        # If it appeared more than once, it is a recurring pattern
        if row.cnt > 1:
            recurring_patterns.append(item)
            # Critical technical patterns: speed, schema, CTR
            if row.pattern_type in ("cwv_pattern", "schema_pattern", "ctr_pattern"):
                critical_structural_patterns.append(item)
            # Recurring unresolved recommendations
            elif row.pattern_type == "recommendation_pattern":
                unresolved_recommendation_patterns.append(item)
                
    return {
        "total_patterns": total_patterns,
        "by_pattern_type": by_pattern_type,
        "top_pattern_labels": top_pattern_labels,
        "recurring_patterns": recurring_patterns,
        "recent_patterns": recent_patterns,
        "critical_structural_patterns": critical_structural_patterns,
        "unresolved_recommendation_patterns": unresolved_recommendation_patterns
    }



