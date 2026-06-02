"""
SEO Intelligence Data Layer Ingestion Service — Phase 22

Provides ingestion, normalization, and derived calculations for GSC, GA4,
and technical audits, caching results cleanly across SQLite and PostgreSQL.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from core.models import (
    ManagedSite,
    SEORawSnapshot,
    SEONormalizedPage,
    SEONormalizedIssue,
    SEOAdvisorRun,
    SEODerivedSignal,
    SEORecommendationMemory
)


def _get_or_create_site(db: Session, site_url: str) -> ManagedSite:
    """Helper to fetch a managed site instance by its clean URL or create one."""
    clean_url = site_url.rstrip("/").lower()
    site = db.query(ManagedSite).filter(ManagedSite.url.like(f"%{clean_url}%")).first()
    
    if not site:
        # Fallback owner (usually default admin user ID 1)
        from core.models import User
        admin = db.query(User).filter(User.role == "admin").first()
        admin_id = admin.id if admin else 1
        
        site = ManagedSite(
            user_id=admin_id,
            name=site_url.replace("https://", "").replace("http://", "").rstrip("/"),
            url=site_url,
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
    signal_data: Dict[str, Any]
) -> SEODerivedSignal:
    """Upsert calculated intelligence signals (quick wins, rank drops, etc.)."""
    site = _get_or_create_site(db, site_url)
    
    # Check if this signal for this entity already exists
    existing = db.query(SEODerivedSignal).filter(
        SEODerivedSignal.site_id == site.id,
        SEODerivedSignal.signal_type == signal_type,
        SEODerivedSignal.entity_identifier == entity_identifier
    ).first()
    
    try:
        data_json = json.dumps(signal_data, ensure_ascii=False)
    except Exception:
        data_json = str(signal_data)
        
    if existing:
        existing.signal_data = data_json
        existing.calculated_at = datetime.now()
        db.commit()
        db.refresh(existing)
        return existing
        
    # Create new signal record
    new_signal = SEODerivedSignal(
        site_id=site.id,
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
    """Track recommendations offered to the user and accumulate optimization outcomes."""
    site = _get_or_create_site(db, site_url)
    
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
