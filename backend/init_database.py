"""
AI Marketing Hub — Database Initializer
========================================
Tạo và chuẩn hóa tất cả SQLite databases cho dự án.

Databases:
  1. sites.db           — Quản lý multi-site
  2. rank_tracker.db    — Theo dõi thứ hạng từ khóa
  3. content_calendar.db — Lịch nội dung
  4. ab_tests.db        — A/B Testing SEO
  5. auth.db            — Hệ thống xác thực JWT
  6. usage_history.db   — Lịch sử sử dụng API

Chạy: python init_database.py
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
import random
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def log(msg: str):
    print(f"  ✅ {msg}")


def warn(msg: str):
    print(f"  ⚠️  {msg}")


def header(msg: str):
    print(f"\n{'─' * 60}")
    print(f"  📦 {msg}")
    print(f"{'─' * 60}")


# ═══════════════════════════════════════════════════════════════
# 1. SITES DATABASE
# ═══════════════════════════════════════════════════════════════

def init_sites_db():
    header("1/6 — sites.db (Quản lý multi-site)")
    db_path = os.path.join(BASE_DIR, "sites.db")
    conn = sqlite3.connect(db_path)
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
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_sites_active
        ON managed_sites(is_active)
    """)
    conn.commit()
    log("Table managed_sites — OK")

    # Sample data
    existing = conn.execute("SELECT COUNT(*) FROM managed_sites").fetchone()[0]
    if existing == 0:
        conn.execute("""
            INSERT INTO managed_sites (name, url, description, niche, is_active, last_scan_score, last_scan_date)
            VALUES (?, ?, ?, ?, 1, 78, ?)
        """, (
            "Mitsubishi Bình Phước",
            "https://binhphuocmitsubishi.com",
            "Đại lý chính hãng Mitsubishi tại Bình Phước",
            "ô tô",
            datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        ))
        conn.commit()
        log("Inserted default site: binhphuocmitsubishi.com")
    else:
        warn(f"Sites DB already has {existing} site(s), skipping sample data")

    conn.close()


# ═══════════════════════════════════════════════════════════════
# 2. RANK TRACKER DATABASE
# ═══════════════════════════════════════════════════════════════

def init_rank_tracker_db():
    header("2/6 — rank_tracker.db (Theo dõi thứ hạng)")
    db_path = os.path.join(BASE_DIR, "rank_tracker.db")
    conn = sqlite3.connect(db_path)
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
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_ranking_site
        ON ranking_history(site_url)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_tracked_site
        ON tracked_keywords(site_url)
    """)
    conn.commit()
    log("Tables tracked_keywords, ranking_history — OK")

    # Sample data
    site_url = "https://binhphuocmitsubishi.com"
    existing = conn.execute("SELECT COUNT(*) FROM tracked_keywords WHERE site_url = ?", (site_url,)).fetchone()[0]
    if existing == 0:
        keywords = [
            ("mitsubishi bình phước", "thương hiệu"),
            ("giá xe xpander 2026", "sản phẩm"),
            ("mitsubishi xpander bình phước", "thương hiệu"),
            ("đại lý mitsubishi bình phước", "thương hiệu"),
            ("xe pajero sport giá tốt", "sản phẩm"),
            ("mua xe trả góp bình phước", "dịch vụ"),
            ("so sánh xpander và rush", "so sánh"),
            ("bảo dưỡng xe mitsubishi", "dịch vụ"),
            ("xe attrage 2026 giá bao nhiêu", "sản phẩm"),
            ("lái thử xe mitsubishi", "dịch vụ"),
        ]
        for kw, tag in keywords:
            conn.execute(
                "INSERT OR IGNORE INTO tracked_keywords (keyword, site_url, tag) VALUES (?, ?, ?)",
                (kw, site_url, tag)
            )
        conn.commit()
        log(f"Inserted {len(keywords)} sample keywords")

        # Generate 30 days of ranking history for each keyword
        now = datetime.now()
        for kw, _ in keywords:
            base_pos = random.uniform(3, 25)
            for day_offset in range(30, -1, -1):
                date = (now - timedelta(days=day_offset)).strftime("%Y-%m-%dT%H:%M:%S")
                pos = max(1, base_pos + random.uniform(-3, 3))
                clicks = max(0, int(random.gauss(15, 8)))
                impressions = max(clicks, int(random.gauss(200, 80)))
                ctr = round((clicks / impressions * 100) if impressions > 0 else 0, 2)
                conn.execute(
                    """INSERT INTO ranking_history (keyword, site_url, position, clicks, impressions, ctr, source, checked_at)
                       VALUES (?, ?, ?, ?, ?, ?, 'sample', ?)""",
                    (kw, site_url, round(pos, 1), clicks, impressions, ctr, date)
                )
            base_pos *= 0.92  # trend upward over time
        conn.commit()
        log(f"Generated 30 days of ranking history ({len(keywords) * 31} records)")
    else:
        warn(f"Rank tracker already has {existing} keyword(s), skipping sample data")

    conn.close()


# ═══════════════════════════════════════════════════════════════
# 3. CONTENT CALENDAR DATABASE
# ═══════════════════════════════════════════════════════════════

def init_content_calendar_db():
    header("3/6 — content_calendar.db (Lịch nội dung)")
    db_path = os.path.join(BASE_DIR, "content_calendar.db")
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS content_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content_type TEXT DEFAULT 'blog',
            status TEXT DEFAULT 'draft',
            scheduled_date TEXT,
            published_date TEXT,
            primary_keyword TEXT DEFAULT '',
            meta_description TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            author TEXT DEFAULT '',
            site_url TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_content_status
        ON content_items(status)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_content_date
        ON content_items(scheduled_date)
    """)
    conn.commit()
    log("Table content_items — OK")

    existing = conn.execute("SELECT COUNT(*) FROM content_items").fetchone()[0]
    if existing == 0:
        now = datetime.now()
        samples = [
            ("Hướng dẫn mua xe Mitsubishi trả góp 2026", "blog", "published", -10, "mua xe trả góp"),
            ("So sánh Xpander vs Toyota Rush — Nên chọn xe nào?", "blog", "published", -5, "so sánh xpander rush"),
            ("Top 5 xe gia đình tốt nhất dưới 700 triệu", "blog", "scheduled", 3, "xe gia đình giá rẻ"),
            ("Bảng giá xe Mitsubishi tháng 6/2026", "page", "draft", 7, "bảng giá mitsubishi"),
            ("Review Pajero Sport 2026 — Có gì mới?", "blog", "idea", 14, "pajero sport 2026"),
            ("Chương trình khuyến mãi hè 2026", "promotion", "scheduled", 5, "khuyến mãi mitsubishi"),
        ]
        for title, ctype, status, day_offset, keyword in samples:
            date = (now + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            published = date if status == "published" else None
            conn.execute("""
                INSERT INTO content_items (title, content_type, status, scheduled_date, published_date, primary_keyword, site_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, ctype, status, date, published, keyword, "https://binhphuocmitsubishi.com"))
        conn.commit()
        log(f"Inserted {len(samples)} sample content items")
    else:
        warn(f"Content calendar already has {existing} item(s), skipping")

    conn.close()


# ═══════════════════════════════════════════════════════════════
# 4. A/B TESTING DATABASE
# ═══════════════════════════════════════════════════════════════

def init_ab_tests_db():
    header("4/6 — ab_tests.db (A/B Testing SEO)")
    db_path = os.path.join(BASE_DIR, "ab_tests.db")
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ab_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url_a TEXT NOT NULL,
            url_b TEXT NOT NULL,
            primary_keyword TEXT DEFAULT '',
            status TEXT DEFAULT 'draft',
            result_a TEXT DEFAULT '{}',
            result_b TEXT DEFAULT '{}',
            winner TEXT DEFAULT '',
            ai_analysis TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            completed_at TEXT
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_ab_status
        ON ab_tests(status)
    """)
    conn.commit()
    log("Table ab_tests — OK")
    conn.close()


# ═══════════════════════════════════════════════════════════════
# 5. AUTH DATABASE
# ═══════════════════════════════════════════════════════════════

def init_auth_db():
    header("5/6 — auth.db (Xác thực JWT)")
    db_path = os.path.join(BASE_DIR, "auth.db")
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT DEFAULT 'viewer',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            last_login TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires_at TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_email
        ON users(email)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_refresh_token
        ON refresh_tokens(token)
    """)
    conn.commit()
    log("Tables users, refresh_tokens — OK")

    # Create default admin if not exists
    existing = conn.execute("SELECT COUNT(*) FROM users WHERE email = 'admin@aimarketing.vn'").fetchone()[0]
    if existing == 0:
        try:
            import bcrypt
            hashed = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        except ImportError:
            # Fallback: simple hash (NOT secure, just for init)
            hashed = hashlib.sha256("admin123".encode()).hexdigest()
            warn("bcrypt not found, using SHA256 fallback for admin password")

        conn.execute("""
            INSERT INTO users (email, full_name, hashed_password, role, is_active)
            VALUES (?, ?, ?, 'admin', 1)
        """, ("admin@aimarketing.vn", "Admin", hashed))
        conn.commit()
        log("Created default admin: admin@aimarketing.vn / admin123")
    else:
        warn("Admin user already exists, skipping")

    conn.close()


# ═══════════════════════════════════════════════════════════════
# 6. USAGE HISTORY DATABASE
# ═══════════════════════════════════════════════════════════════

def init_usage_history_db():
    header("6/6 — usage_history.db (Lịch sử API)")
    db_path = os.path.join(BASE_DIR, "data", "usage_history.db")
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT NOT NULL,
            method TEXT DEFAULT 'POST',
            input_data TEXT,
            output_data TEXT,
            status_code INTEGER DEFAULT 200,
            duration_ms REAL DEFAULT 0,
            error TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_usage_endpoint
        ON usage_log(endpoint)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_usage_date
        ON usage_log(created_at)
    """)
    conn.commit()
    log("Table usage_log — OK")
    conn.close()


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  🚀 AI Marketing Hub — Database Initializer")
    print("=" * 60)
    print(f"  📂 Base directory: {BASE_DIR}")
    print(f"  🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    init_sites_db()
    init_rank_tracker_db()
    init_content_calendar_db()
    init_ab_tests_db()
    init_auth_db()
    init_usage_history_db()

    # Summary
    print(f"\n{'═' * 60}")
    print("  🎉 DATABASE INITIALIZATION COMPLETE!")
    print(f"{'═' * 60}")
    dbs = [
        ("sites.db", os.path.join(BASE_DIR, "sites.db")),
        ("rank_tracker.db", os.path.join(BASE_DIR, "rank_tracker.db")),
        ("content_calendar.db", os.path.join(BASE_DIR, "content_calendar.db")),
        ("ab_tests.db", os.path.join(BASE_DIR, "ab_tests.db")),
        ("auth.db", os.path.join(BASE_DIR, "auth.db")),
        ("data/usage_history.db", os.path.join(BASE_DIR, "data", "usage_history.db")),
    ]
    for name, path in dbs:
        size = os.path.getsize(path) if os.path.exists(path) else 0
        print(f"  📄 {name:30s} {size / 1024:.1f} KB")
    print()


if __name__ == "__main__":
    main()
