"""
Content Calendar — Phase 15 (SQLAlchemy)

Manage content publishing schedule with:
- Calendar view (monthly/weekly)
- Status tracking: Draft → Review → Published
- AI topic suggestions based on trending + keyword gaps
- Deadline reminders
"""

import os
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import httpx

from core.database import SessionLocal
from core.models import ManagedSite, ContentItem

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _get_site_id(db, site_url: str) -> int:
    site = db.query(ManagedSite).filter(ManagedSite.url == site_url).first()
    if not site:
        raise ValueError(f"Site {site_url} không tồn tại")
    return site.id


def add_item(
    title: str,
    site_url: str,
    description: str = "",
    content_type: str = "blog",
    scheduled_date: str = "",
    author: str = "",
    keywords: str = "",
    priority: str = "medium",  # Note: Priority is kept in notes or we can just ignore it for now as it's not in the model, actually I will add it to notes
) -> Dict[str, Any]:
    """Add a content calendar item."""
    db = SessionLocal()
    try:
        site_id = _get_site_id(db, site_url)
        
        # We store description and priority in 'notes' as JSON or simple string, 
        # but the old schema had description and priority. 
        # The new SQLAlchemy model has 'meta_description', 'notes', 'primary_keyword'.
        # We will map keywords -> primary_keyword, description/priority -> notes
        
        item = ContentItem(
            site_id=site_id,
            title=title.strip(),
            content_type=content_type,
            status="draft",
            scheduled_date=scheduled_date,
            primary_keyword=keywords,
            meta_description=description.strip(),
            author=author,
            notes=f"Priority: {priority}"
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return {"status": "ok", "id": item.id, "title": item.title}
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def update_item(item_id: int, **kwargs) -> Dict[str, Any]:
    """Update a calendar item."""
    db = SessionLocal()
    try:
        item = db.query(ContentItem).filter(ContentItem.id == item_id).first()
        if not item:
            return {"status": "error", "message": "Item not found"}

        # Map kwargs to model fields
        mapping = {
            "title": "title",
            "description": "meta_description",
            "content_type": "content_type",
            "status": "status",
            "scheduled_date": "scheduled_date",
            "published_date": "published_date",
            "author": "author",
            "keywords": "primary_keyword",
            "notes": "notes"
        }
        
        updated_fields = []
        for k, v in kwargs.items():
            if k in mapping and v is not None:
                setattr(item, mapping[k], v)
                updated_fields.append(k)
        
        if not updated_fields:
            return {"status": "error", "message": "Không có gì để cập nhật"}

        db.commit()
        return {"status": "ok", "id": item_id, "updated": updated_fields}
    finally:
        db.close()


def delete_item(item_id: int) -> Dict[str, Any]:
    """Delete a calendar item."""
    db = SessionLocal()
    try:
        item = db.query(ContentItem).filter(ContentItem.id == item_id).first()
        if item:
            db.delete(item)
            db.commit()
            return {"status": "ok", "deleted": item_id}
        return {"status": "error", "message": "Item not found"}
    finally:
        db.close()


def get_items(
    site_url: str,
    month: str = "",
    status: str = "",
    content_type: str = "",
) -> List[Dict[str, Any]]:
    """Get calendar items with optional filters."""
    db = SessionLocal()
    try:
        site_id = _get_site_id(db, site_url)
        query = db.query(ContentItem).filter(ContentItem.site_id == site_id)

        if month:
            query = query.filter(ContentItem.scheduled_date.like(f"{month}%"))
        if status:
            query = query.filter(ContentItem.status == status)
        if content_type:
            query = query.filter(ContentItem.content_type == content_type)

        # Basic order by scheduled_date
        items = query.order_by(ContentItem.scheduled_date.asc()).all()
        
        return [{
            "id": i.id,
            "title": i.title,
            "description": i.meta_description,
            "content_type": i.content_type,
            "status": i.status,
            "scheduled_date": i.scheduled_date,
            "published_date": i.published_date,
            "author": i.author,
            "keywords": i.primary_keyword,
            "notes": i.notes,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None
        } for i in items]
    except ValueError:
        return []
    finally:
        db.close()


def get_stats(site_url: str) -> Dict[str, Any]:
    """Get calendar statistics."""
    db = SessionLocal()
    try:
        site_id = _get_site_id(db, site_url)
        
        total = db.query(ContentItem).filter(ContentItem.site_id == site_id).count()
        draft = db.query(ContentItem).filter(ContentItem.site_id == site_id, ContentItem.status == 'draft').count()
        review = db.query(ContentItem).filter(ContentItem.site_id == site_id, ContentItem.status == 'review').count()
        published = db.query(ContentItem).filter(ContentItem.site_id == site_id, ContentItem.status == 'published').count()

        # Upcoming deadlines (next 7 days)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        week_later = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%d")
        
        upcoming = db.query(ContentItem).filter(
            ContentItem.site_id == site_id,
            ContentItem.scheduled_date >= today,
            ContentItem.scheduled_date <= week_later,
            ContentItem.status != 'published'
        ).count()

        # Overdue
        overdue = db.query(ContentItem).filter(
            ContentItem.site_id == site_id,
            ContentItem.scheduled_date < today,
            ContentItem.status != 'published'
        ).count()

        return {
            "total": total, "draft": draft, "review": review,
            "published": published, "upcoming": upcoming, "overdue": overdue,
        }
    except ValueError:
        return {
            "total": 0, "draft": 0, "review": 0,
            "published": 0, "upcoming": 0, "overdue": 0,
        }
    finally:
        db.close()


async def suggest_topics(site_url: str, niche: str = "ô tô", count: int = 5) -> Dict[str, Any]:
    """AI-powered topic suggestions."""
    if not GROQ_API_KEY:
        return {"error": "Chưa cấu hình GROQ_API_KEY"}

    prompt = f"""Bạn là chuyên gia content marketing cho ngành {niche}.
Đề xuất {count} chủ đề bài viết blog cho website {site_url}.

Yêu cầu:
- Mỗi chủ đề có: title, description (1 câu), content_type (blog/guide/comparison/news), priority (high/medium/low), keywords (3 từ khóa)
- Chọn chủ đề có search volume cao, dễ rank
- Phù hợp xu hướng hiện tại
- Trả về JSON array

Format:
[{{"title": "...", "description": "...", "content_type": "...", "priority": "...", "keywords": "kw1, kw2, kw3"}}]

Chỉ trả về JSON, không giải thích."""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
            )
            if resp.status_code != 200:
                return {"error": f"AI lỗi: {resp.status_code}"}

            import re
            ai_text = resp.json()["choices"][0]["message"]["content"].strip()
            match = re.search(r'\[.*\]', ai_text, re.DOTALL)
            if match:
                topics = json.loads(match.group())
                return {"topics": topics, "total": len(topics)}
            return {"error": "AI không trả về JSON hợp lệ"}
    except Exception as e:
        return {"error": str(e)}
