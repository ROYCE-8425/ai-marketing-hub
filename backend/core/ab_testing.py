"""
SEO A/B Testing — Phase 19

Create and evaluate A/B tests for SEO elements:
- Title tag testing
- Meta description testing
- Content heading testing
- AI-powered evaluation of variants
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "ab_tests.db")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ab_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            test_type TEXT DEFAULT 'title',
            url TEXT DEFAULT '',
            keyword TEXT DEFAULT '',
            variant_a TEXT NOT NULL,
            variant_b TEXT NOT NULL,
            winner TEXT DEFAULT '',
            ai_analysis TEXT DEFAULT '',
            score_a REAL DEFAULT 0,
            score_b REAL DEFAULT 0,
            status TEXT DEFAULT 'pending',
            site_url TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            evaluated_at TEXT
        )
    """)
    conn.commit()
    return conn


def create_test(
    name: str,
    test_type: str,
    variant_a: str,
    variant_b: str,
    site_url: str,
    url: str = "",
    keyword: str = "",
) -> Dict[str, Any]:
    """Create a new A/B test."""
    conn = _get_db()
    try:
        cursor = conn.execute(
            """INSERT INTO ab_tests (name, test_type, variant_a, variant_b, url, keyword, site_url)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name.strip(), test_type, variant_a.strip(), variant_b.strip(), url, keyword, site_url),
        )
        conn.commit()
        return {"status": "ok", "id": cursor.lastrowid, "name": name.strip()}
    finally:
        conn.close()


def get_tests(site_url: str, status: str = "") -> List[Dict[str, Any]]:
    """Get all A/B tests."""
    conn = _get_db()
    try:
        query = "SELECT * FROM ab_tests WHERE site_url = ?"
        params: list = [site_url]
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_test(test_id: int) -> Dict[str, Any]:
    """Delete an A/B test."""
    conn = _get_db()
    try:
        conn.execute("DELETE FROM ab_tests WHERE id = ?", (test_id,))
        conn.commit()
        return {"status": "ok", "deleted": test_id}
    finally:
        conn.close()


async def evaluate_test(test_id: int) -> Dict[str, Any]:
    """AI-evaluate an A/B test and determine winner."""
    conn = _get_db()
    try:
        row = conn.execute("SELECT * FROM ab_tests WHERE id = ?", (test_id,)).fetchone()
        if not row:
            return {"error": "Test không tồn tại"}

        test = dict(row)
    finally:
        conn.close()

    if not GROQ_API_KEY:
        return {"error": "Chưa cấu hình GROQ_API_KEY"}

    type_labels = {
        "title": "Title tag (thẻ tiêu đề SEO)",
        "description": "Meta description",
        "heading": "Heading (H1/H2)",
        "content": "Nội dung bài viết",
    }
    type_label = type_labels.get(test["test_type"], test["test_type"])

    prompt = f"""Bạn là chuyên gia SEO. So sánh 2 phiên bản {type_label} và chọn bản tốt hơn.

URL: {test.get('url', 'N/A')}
Từ khóa mục tiêu: {test.get('keyword', 'N/A')}

PHIÊN BẢN A:
{test['variant_a']}

PHIÊN BẢN B:
{test['variant_b']}

Phân tích theo các tiêu chí:
1. SEO (keyword placement, length, relevance)
2. CTR (hấp dẫn, gây tò mò, power words)
3. User Intent (phù hợp search intent)
4. Độ tự nhiên (không spam, đọc tốt)

Trả về JSON format:
{{
  "winner": "A" hoặc "B",
  "score_a": 0-100,
  "score_b": 0-100,
  "analysis": "Phân tích chi tiết...",
  "criteria": {{
    "seo": {{"a": 0-25, "b": 0-25, "note": "..."}},
    "ctr": {{"a": 0-25, "b": 0-25, "note": "..."}},
    "intent": {{"a": 0-25, "b": 0-25, "note": "..."}},
    "natural": {{"a": 0-25, "b": 0-25, "note": "..."}}
  }}
}}

Chỉ trả về JSON."""

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
                    "temperature": 0.3,
                    "max_tokens": 1024,
                },
            )
            if resp.status_code != 200:
                return {"error": f"AI lỗi: {resp.status_code}"}

            import re
            ai_text = resp.json()["choices"][0]["message"]["content"].strip()
            match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if not match:
                return {"error": "AI không trả về JSON hợp lệ"}

            result = json.loads(match.group())

            # Save results
            conn = _get_db()
            try:
                conn.execute(
                    """UPDATE ab_tests SET
                       winner = ?, score_a = ?, score_b = ?,
                       ai_analysis = ?, status = 'evaluated', evaluated_at = ?
                       WHERE id = ?""",
                    (
                        result.get("winner", ""),
                        result.get("score_a", 0),
                        result.get("score_b", 0),
                        json.dumps(result, ensure_ascii=False),
                        datetime.utcnow().isoformat(),
                        test_id,
                    ),
                )
                conn.commit()
            finally:
                conn.close()

            return {
                "status": "ok",
                "test_id": test_id,
                "winner": result.get("winner"),
                "score_a": result.get("score_a"),
                "score_b": result.get("score_b"),
                "analysis": result.get("analysis"),
                "criteria": result.get("criteria", {}),
            }

    except Exception as e:
        return {"error": str(e)}
