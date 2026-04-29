"""
Content Calendar — Phase 15

Manage content publishing schedule with:
- Calendar view (monthly/weekly)
- Status tracking: Draft → Review → Published
- AI topic suggestions based on trending + keyword gaps
- Deadline reminders
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "content_calendar.db")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS calendar_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            content_type TEXT DEFAULT 'blog',
            status TEXT DEFAULT 'draft',
            scheduled_date TEXT,
            published_date TEXT,
            author TEXT DEFAULT '',
            keywords TEXT DEFAULT '',
            site_url TEXT NOT NULL,
            notes TEXT DEFAULT '',
            priority TEXT DEFAULT 'medium',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    return conn


def add_item(
    title: str,
    site_url: str,
    description: str = "",
    content_type: str = "blog",
    scheduled_date: str = "",
    author: str = "",
    keywords: str = "",
    priority: str = "medium",
) -> Dict[str, Any]:
    """Add a content calendar item."""
    conn = _get_db()
    try:
        cursor = conn.execute(
            """INSERT INTO calendar_items
               (title, description, content_type, scheduled_date, author, keywords, site_url, priority)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (title.strip(), description.strip(), content_type, scheduled_date, author, keywords, site_url, priority),
        )
        conn.commit()
        return {"status": "ok", "id": cursor.lastrowid, "title": title.strip()}
    finally:
        conn.close()


def update_item(item_id: int, **kwargs) -> Dict[str, Any]:
    """Update a calendar item."""
    conn = _get_db()
    try:
        allowed = {"title", "description", "content_type", "status", "scheduled_date",
                    "published_date", "author", "keywords", "notes", "priority"}
        updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if not updates:
            return {"status": "error", "message": "Không có gì để cập nhật"}

        updates["updated_at"] = datetime.utcnow().isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [item_id]

        conn.execute(f"UPDATE calendar_items SET {set_clause} WHERE id = ?", values)
        conn.commit()
        return {"status": "ok", "id": item_id, "updated": list(updates.keys())}
    finally:
        conn.close()


def delete_item(item_id: int) -> Dict[str, Any]:
    """Delete a calendar item."""
    conn = _get_db()
    try:
        conn.execute("DELETE FROM calendar_items WHERE id = ?", (item_id,))
        conn.commit()
        return {"status": "ok", "deleted": item_id}
    finally:
        conn.close()


def get_items(
    site_url: str,
    month: str = "",
    status: str = "",
    content_type: str = "",
) -> List[Dict[str, Any]]:
    """Get calendar items with optional filters."""
    conn = _get_db()
    try:
        query = "SELECT * FROM calendar_items WHERE site_url = ?"
        params: list = [site_url]

        if month:
            query += " AND scheduled_date LIKE ?"
            params.append(f"{month}%")

        if status:
            query += " AND status = ?"
            params.append(status)

        if content_type:
            query += " AND content_type = ?"
            params.append(content_type)

        query += " ORDER BY scheduled_date ASC, priority DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_stats(site_url: str) -> Dict[str, Any]:
    """Get calendar statistics."""
    conn = _get_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM calendar_items WHERE site_url = ?", (site_url,)).fetchone()[0]
        draft = conn.execute("SELECT COUNT(*) FROM calendar_items WHERE site_url = ? AND status = 'draft'", (site_url,)).fetchone()[0]
        review = conn.execute("SELECT COUNT(*) FROM calendar_items WHERE site_url = ? AND status = 'review'", (site_url,)).fetchone()[0]
        published = conn.execute("SELECT COUNT(*) FROM calendar_items WHERE site_url = ? AND status = 'published'", (site_url,)).fetchone()[0]

        # Upcoming deadlines (next 7 days)
        today = datetime.utcnow().strftime("%Y-%m-%d")
        week_later = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d")
        upcoming = conn.execute(
            "SELECT COUNT(*) FROM calendar_items WHERE site_url = ? AND scheduled_date BETWEEN ? AND ? AND status != 'published'",
            (site_url, today, week_later),
        ).fetchone()[0]

        # Overdue
        overdue = conn.execute(
            "SELECT COUNT(*) FROM calendar_items WHERE site_url = ? AND scheduled_date < ? AND status != 'published'",
            (site_url, today),
        ).fetchone()[0]

        return {
            "total": total, "draft": draft, "review": review,
            "published": published, "upcoming": upcoming, "overdue": overdue,
        }
    finally:
        conn.close()


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
