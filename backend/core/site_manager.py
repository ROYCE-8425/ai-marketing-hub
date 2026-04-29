"""
Multi-site Manager — Phase 18

Manage multiple websites from a single dashboard:
- Add/remove/list sites
- Switch active site context
- Compare SEO scores across sites
"""

import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "sites.db")


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS managed_sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            niche TEXT DEFAULT '',
            is_active INTEGER DEFAULT 0,
            last_scan_score INTEGER DEFAULT 0,
            last_scan_date TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    return conn


def add_site(name: str, url: str, description: str = "", niche: str = "") -> Dict[str, Any]:
    """Add a new site to manage."""
    conn = _get_db()
    try:
        # Normalize URL
        url = url.strip().rstrip("/")
        if not url.startswith("http"):
            url = f"https://{url}"

        cursor = conn.execute(
            "INSERT OR IGNORE INTO managed_sites (name, url, description, niche) VALUES (?, ?, ?, ?)",
            (name.strip(), url, description.strip(), niche.strip()),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return {"status": "exists", "message": f"Site {url} đã tồn tại"}
        return {"status": "ok", "id": cursor.lastrowid, "name": name.strip(), "url": url}
    finally:
        conn.close()


def remove_site(site_id: int) -> Dict[str, Any]:
    """Remove a site."""
    conn = _get_db()
    try:
        conn.execute("DELETE FROM managed_sites WHERE id = ?", (site_id,))
        conn.commit()
        return {"status": "ok", "deleted": site_id}
    finally:
        conn.close()


def get_sites() -> List[Dict[str, Any]]:
    """Get all managed sites."""
    conn = _get_db()
    try:
        rows = conn.execute("SELECT * FROM managed_sites ORDER BY is_active DESC, name ASC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def set_active_site(site_id: int) -> Dict[str, Any]:
    """Set a site as active (deactivate others)."""
    conn = _get_db()
    try:
        conn.execute("UPDATE managed_sites SET is_active = 0")
        conn.execute("UPDATE managed_sites SET is_active = 1 WHERE id = ?", (site_id,))
        conn.commit()
        row = conn.execute("SELECT * FROM managed_sites WHERE id = ?", (site_id,)).fetchone()
        if row:
            return {"status": "ok", "active_site": dict(row)}
        return {"status": "error", "message": "Site không tồn tại"}
    finally:
        conn.close()


def get_active_site() -> Dict[str, Any]:
    """Get current active site."""
    conn = _get_db()
    try:
        row = conn.execute("SELECT * FROM managed_sites WHERE is_active = 1").fetchone()
        if row:
            return dict(row)
        # If no active site, return first one
        row = conn.execute("SELECT * FROM managed_sites ORDER BY id ASC LIMIT 1").fetchone()
        if row:
            return dict(row)
        return {"url": "https://binhphuocmitsubishi.com", "name": "Default"}
    finally:
        conn.close()


def update_scan_score(site_id: int, score: int) -> Dict[str, Any]:
    """Update last scan score for a site."""
    conn = _get_db()
    try:
        conn.execute(
            "UPDATE managed_sites SET last_scan_score = ?, last_scan_date = ? WHERE id = ?",
            (score, datetime.utcnow().isoformat(), site_id),
        )
        conn.commit()
        return {"status": "ok"}
    finally:
        conn.close()
