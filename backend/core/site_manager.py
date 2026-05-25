"""
Multi-site Manager — Phase 18 (SQLAlchemy)

Manage multiple websites from a single dashboard:
- Add/remove/list sites
- Switch active site context
- Compare SEO scores across sites
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from core.database import SessionLocal
from core.models import ManagedSite

def add_site(name: str, url: str, description: str = "", niche: str = "", user_id: int = 1) -> Dict[str, Any]:
    """Add a new site to manage. Defaults to user_id=1 (admin) if not provided."""
    db = SessionLocal()
    try:
        # Normalize URL
        url = url.strip().rstrip("/")
        if not url.startswith("http"):
            url = f"https://{url}"

        existing = db.query(ManagedSite).filter(ManagedSite.url == url).first()
        if existing:
            return {"status": "exists", "message": f"Site {url} đã tồn tại"}

        new_site = ManagedSite(
            user_id=user_id,
            name=name.strip(),
            url=url,
            description=description.strip(),
            niche=niche.strip()
        )
        db.add(new_site)
        db.commit()
        db.refresh(new_site)
        return {"status": "ok", "id": new_site.id, "name": new_site.name, "url": new_site.url}
    finally:
        db.close()


def remove_site(site_id: int) -> Dict[str, Any]:
    """Remove a site."""
    db = SessionLocal()
    try:
        site = db.query(ManagedSite).filter(ManagedSite.id == site_id).first()
        if site:
            db.delete(site)
            db.commit()
            return {"status": "ok", "deleted": site_id}
        return {"status": "error", "message": "Site not found"}
    finally:
        db.close()


def get_sites() -> List[Dict[str, Any]]:
    """Get all managed sites."""
    db = SessionLocal()
    try:
        sites = db.query(ManagedSite).order_by(ManagedSite.is_active.desc(), ManagedSite.name.asc()).all()
        return [{
            "id": s.id,
            "user_id": s.user_id,
            "name": s.name,
            "url": s.url,
            "description": s.description,
            "niche": s.niche,
            "is_active": s.is_active,
            "last_scan_score": s.last_scan_score,
            "last_scan_date": s.last_scan_date.isoformat() if s.last_scan_date else None,
            "created_at": s.created_at.isoformat() if s.created_at else None
        } for s in sites]
    finally:
        db.close()


def set_active_site(site_id: int) -> Dict[str, Any]:
    """Set a site as active (deactivate others)."""
    db = SessionLocal()
    try:
        # Deactivate all
        db.query(ManagedSite).update({"is_active": False})
        
        # Activate target
        site = db.query(ManagedSite).filter(ManagedSite.id == site_id).first()
        if site:
            site.is_active = True
            db.commit()
            return {"status": "ok", "active_site": {
                "id": site.id, "name": site.name, "url": site.url, "is_active": site.is_active
            }}
        db.commit() # Commit the deactivations anyway
        return {"status": "error", "message": "Site không tồn tại"}
    finally:
        db.close()


def get_active_site() -> Dict[str, Any]:
    """Get current active site."""
    db = SessionLocal()
    try:
        site = db.query(ManagedSite).filter(ManagedSite.is_active == True).first()
        if site:
            return {
                "id": site.id, "name": site.name, "url": site.url, 
                "description": site.description, "niche": site.niche,
                "is_active": site.is_active, "last_scan_score": site.last_scan_score
            }
        
        # If no active site, return first one
        first_site = db.query(ManagedSite).order_by(ManagedSite.id.asc()).first()
        if first_site:
            return {
                "id": first_site.id, "name": first_site.name, "url": first_site.url, 
                "description": first_site.description, "niche": first_site.niche,
                "is_active": first_site.is_active, "last_scan_score": first_site.last_scan_score
            }
        
        return {"url": "", "name": "", "status": "not_configured", "message": "Chưa có site nào. Thêm site trong Quản lý site."}
    finally:
        db.close()


def update_scan_score(site_id: int, score: int) -> Dict[str, Any]:
    """Update last scan score for a site."""
    db = SessionLocal()
    try:
        site = db.query(ManagedSite).filter(ManagedSite.id == site_id).first()
        if site:
            site.last_scan_score = score
            site.last_scan_date = datetime.now(timezone.utc)
            db.commit()
            return {"status": "ok"}
        return {"status": "error", "message": "Site not found"}
    finally:
        db.close()
