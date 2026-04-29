"""
Keyword Rank Tracker — Phase 10 (Upgraded)

Tracks keyword ranking positions over time using:
1. Google Search Console API (free, already configured)
2. DataForSEO API (optional, when configured)

Features:
- SQLite history with trend charts
- Tag/group keywords by campaign
- CSV import/export
- Ranking drop alerts
"""

import os
import io
import csv
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "rank_tracker.db")


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tracked_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            site_url TEXT NOT NULL,
            tag TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(keyword, site_url)
        )
    """)
    # Add tag column if missing (migration for existing DBs)
    try:
        conn.execute("ALTER TABLE tracked_keywords ADD COLUMN tag TEXT DEFAULT ''")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # column already exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ranking_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            site_url TEXT NOT NULL,
            position REAL,
            clicks INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            ctr REAL DEFAULT 0,
            source TEXT DEFAULT 'gsc',
            checked_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_ranking_keyword_date
        ON ranking_history(keyword, checked_at)
    """)
    conn.commit()
    return conn


def add_keyword(keyword: str, site_url: str, tag: str = "") -> Dict[str, Any]:
    """Add a keyword to track."""
    conn = _get_db()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO tracked_keywords (keyword, site_url, tag) VALUES (?, ?, ?)",
            (keyword.strip().lower(), site_url, tag.strip()),
        )
        conn.commit()
        return {"status": "ok", "keyword": keyword.strip().lower(), "tag": tag.strip()}
    finally:
        conn.close()


def update_keyword_tag(keyword: str, site_url: str, tag: str) -> Dict[str, Any]:
    """Update tag for a tracked keyword."""
    conn = _get_db()
    try:
        conn.execute(
            "UPDATE tracked_keywords SET tag = ? WHERE keyword = ? AND site_url = ?",
            (tag.strip(), keyword.strip().lower(), site_url),
        )
        conn.commit()
        return {"status": "ok", "keyword": keyword.strip().lower(), "tag": tag.strip()}
    finally:
        conn.close()


def remove_keyword(keyword: str, site_url: str) -> Dict[str, Any]:
    """Remove a tracked keyword."""
    conn = _get_db()
    try:
        kw = keyword.strip().lower()
        conn.execute(
            "DELETE FROM tracked_keywords WHERE keyword = ? AND site_url = ?",
            (kw, site_url),
        )
        conn.execute(
            "DELETE FROM ranking_history WHERE keyword = ? AND site_url = ?",
            (kw, site_url),
        )
        conn.commit()
        return {"status": "ok", "removed": kw}
    finally:
        conn.close()


def get_tracked_keywords(site_url: str, tag_filter: str = "") -> List[Dict[str, Any]]:
    """Get all tracked keywords with latest ranking."""
    conn = _get_db()
    try:
        query = """
            SELECT tk.keyword, tk.tag, tk.created_at,
                   rh.position, rh.clicks, rh.impressions, rh.ctr, rh.source, rh.checked_at,
                   prev.position as prev_position
            FROM tracked_keywords tk
            LEFT JOIN (
                SELECT keyword, site_url, position, clicks, impressions, ctr, source, checked_at,
                       ROW_NUMBER() OVER (PARTITION BY keyword ORDER BY checked_at DESC) as rn
                FROM ranking_history
            ) rh ON rh.keyword = tk.keyword AND rh.site_url = tk.site_url AND rh.rn = 1
            LEFT JOIN (
                SELECT keyword, site_url, position,
                       ROW_NUMBER() OVER (PARTITION BY keyword ORDER BY checked_at DESC) as rn
                FROM ranking_history
            ) prev ON prev.keyword = tk.keyword AND prev.site_url = tk.site_url AND prev.rn = 2
            WHERE tk.site_url = ?
        """
        params: list = [site_url]
        if tag_filter:
            query += " AND tk.tag = ?"
            params.append(tag_filter)
        query += " ORDER BY rh.position ASC NULLS LAST"

        rows = conn.execute(query, params).fetchall()

        results = []
        for r in rows:
            pos = r["position"]
            prev_pos = r["prev_position"]
            change = None
            if pos is not None and prev_pos is not None:
                change = round(prev_pos - pos, 1)  # positive = improved

            results.append({
                "keyword": r["keyword"],
                "tag": r["tag"] or "",
                "position": pos,
                "previous_position": prev_pos,
                "change": change,
                "clicks": r["clicks"] or 0,
                "impressions": r["impressions"] or 0,
                "ctr": r["ctr"] or 0,
                "source": r["source"] or "pending",
                "last_checked": r["checked_at"],
                "created_at": r["created_at"],
            })
        return results
    finally:
        conn.close()


def get_all_tags(site_url: str) -> List[str]:
    """Get all unique tags."""
    conn = _get_db()
    try:
        rows = conn.execute(
            "SELECT DISTINCT tag FROM tracked_keywords WHERE site_url = ? AND tag != ''",
            (site_url,),
        ).fetchall()
        return [r["tag"] for r in rows]
    finally:
        conn.close()


def import_keywords_csv(csv_text: str, site_url: str) -> Dict[str, Any]:
    """Import keywords from CSV text. Columns: keyword, tag (optional)."""
    conn = _get_db()
    try:
        reader = csv.reader(io.StringIO(csv_text.strip()))
        added = 0
        skipped = 0
        for row in reader:
            if not row or not row[0].strip():
                continue
            kw = row[0].strip().lower()
            tag = row[1].strip() if len(row) > 1 else ""
            # Skip header row
            if kw in ("keyword", "từ khóa", "tu khoa"):
                continue
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO tracked_keywords (keyword, site_url, tag) VALUES (?, ?, ?)",
                    (kw, site_url, tag),
                )
                added += 1
            except Exception:
                skipped += 1
        conn.commit()
        return {"status": "ok", "added": added, "skipped": skipped}
    finally:
        conn.close()


def export_keywords_csv(site_url: str) -> str:
    """Export tracked keywords with latest rankings as CSV."""
    keywords = get_tracked_keywords(site_url)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Keyword", "Tag", "Vị trí", "Thay đổi", "Clicks", "Hiển thị", "CTR", "Nguồn", "Cập nhật"])
    for kw in keywords:
        writer.writerow([
            kw["keyword"], kw.get("tag", ""),
            kw["position"] or "—", kw["change"] or "—",
            kw["clicks"], kw["impressions"],
            f"{kw['ctr']}%" if kw["ctr"] else "—",
            kw["source"], kw["last_checked"] or "—",
        ])
    return output.getvalue()


def check_ranking_alerts(site_url: str, threshold: int = 5) -> List[Dict[str, Any]]:
    """Check for keywords that dropped more than threshold positions."""
    keywords = get_tracked_keywords(site_url)
    alerts = []
    for kw in keywords:
        if kw["change"] is not None and kw["change"] < -threshold:
            alerts.append({
                "keyword": kw["keyword"],
                "current_position": kw["position"],
                "previous_position": kw["previous_position"],
                "drop": abs(kw["change"]),
                "severity": "critical" if kw["change"] < -10 else "warning",
            })
    return alerts


def get_keyword_history(keyword: str, site_url: str, days: int = 30) -> List[Dict[str, Any]]:
    """Get ranking history for a keyword."""
    conn = _get_db()
    try:
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        rows = conn.execute(
            """
            SELECT position, clicks, impressions, ctr, source, checked_at
            FROM ranking_history
            WHERE keyword = ? AND site_url = ? AND checked_at >= ?
            ORDER BY checked_at ASC
            """,
            (keyword.strip().lower(), site_url, since),
        ).fetchall()

        return [
            {
                "date": r["checked_at"][:10],
                "position": r["position"],
                "clicks": r["clicks"],
                "impressions": r["impressions"],
                "ctr": r["ctr"],
                "source": r["source"],
            }
            for r in rows
        ]
    finally:
        conn.close()


def save_ranking(keyword: str, site_url: str, position: float,
                 clicks: int = 0, impressions: int = 0, ctr: float = 0,
                 source: str = "gsc") -> None:
    """Save a ranking data point."""
    conn = _get_db()
    try:
        conn.execute(
            """INSERT INTO ranking_history (keyword, site_url, position, clicks, impressions, ctr, source)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (keyword.strip().lower(), site_url, position, clicks, impressions, ctr, source),
        )
        conn.commit()
    finally:
        conn.close()


async def sync_rankings_from_gsc(site_url: str) -> Dict[str, Any]:
    """Fetch current rankings from Google Search Console and save to DB."""
    import httpx

    client_id = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET", "")
    refresh_token = os.getenv("GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN", "")
    gsc_site = os.getenv("GSC_SITE_URL", site_url)

    if not all([client_id, client_secret, refresh_token]):
        return {"error": "GSC chưa cấu hình OAuth2", "synced": 0}

    # Get access token
    async with httpx.AsyncClient(timeout=15) as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if token_resp.status_code != 200:
            return {"error": "Không thể refresh token GSC", "synced": 0}

        access_token = token_resp.json().get("access_token")

        # Get tracked keywords
        conn = _get_db()
        tracked = conn.execute(
            "SELECT keyword FROM tracked_keywords WHERE site_url = ?",
            (site_url,),
        ).fetchall()
        conn.close()

        if not tracked:
            return {"error": "Chưa có keyword nào được theo dõi", "synced": 0}

        keywords = [r["keyword"] for r in tracked]
        synced_count = 0

        # Query GSC for each keyword
        for kw in keywords:
            try:
                resp = await client.post(
                    f"https://www.googleapis.com/webmasters/v3/sites/{gsc_site}/searchAnalytics/query",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={
                        "startDate": (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d"),
                        "endDate": datetime.utcnow().strftime("%Y-%m-%d"),
                        "dimensions": ["query"],
                        "dimensionFilterGroups": [{
                            "filters": [{
                                "dimension": "query",
                                "expression": kw,
                                "operator": "equals",
                            }]
                        }],
                        "rowLimit": 1,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    rows = data.get("rows", [])
                    if rows:
                        row = rows[0]
                        save_ranking(
                            keyword=kw,
                            site_url=site_url,
                            position=round(row.get("position", 0), 1),
                            clicks=row.get("clicks", 0),
                            impressions=row.get("impressions", 0),
                            ctr=round(row.get("ctr", 0) * 100, 2),
                            source="gsc",
                        )
                        synced_count += 1
                    else:
                        # Keyword not found in GSC — save as position 0
                        save_ranking(kw, site_url, 0, source="gsc_not_found")
                        synced_count += 1
            except Exception:
                continue

        return {"status": "ok", "synced": synced_count, "total_keywords": len(keywords)}
