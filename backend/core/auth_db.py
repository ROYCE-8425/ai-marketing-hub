"""
Auth database — SQLite storage for users & refresh tokens.

Tables:
  - users (id, email, full_name, hashed_password, role, is_active, created_at, last_login)
  - refresh_tokens (id, user_id, token, expires_at, created_at)

Auto-creates default admin on first run:
  email: admin@aimarketing.vn  |  password: admin123  |  role: admin
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from core.auth import hash_password

# ── DB path (next to backend root) ──────────────────────────────────────────

_DB_DIR = os.path.dirname(os.path.dirname(__file__))
_DB_PATH = os.path.join(_DB_DIR, "auth.db")


def _get_conn() -> sqlite3.Connection:
    """Get a SQLite connection with row_factory for dict-like access."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ── Schema init ──────────────────────────────────────────────────────────────

def _init_db():
    """Create tables if they don't exist and seed default admin."""
    conn = _get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                email           TEXT    UNIQUE NOT NULL,
                full_name       TEXT    NOT NULL,
                hashed_password TEXT    NOT NULL,
                role            TEXT    NOT NULL DEFAULT 'viewer',
                is_active       INTEGER NOT NULL DEFAULT 1,
                created_at      TEXT    NOT NULL,
                last_login      TEXT
            );

            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                token       TEXT    UNIQUE NOT NULL,
                expires_at  TEXT    NOT NULL,
                created_at  TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            CREATE INDEX IF NOT EXISTS idx_refresh_user ON refresh_tokens(user_id);
            CREATE INDEX IF NOT EXISTS idx_refresh_token ON refresh_tokens(token);
        """)

        # Seed default admin if table is empty
        row = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
        if row["cnt"] == 0:
            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "INSERT INTO users (email, full_name, hashed_password, role, is_active, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    "admin@aimarketing.vn",
                    "Admin",
                    hash_password("admin123"),
                    "admin",
                    1,
                    now,
                ),
            )
            conn.commit()
    finally:
        conn.close()


# Run on import
_init_db()


# ── User CRUD ────────────────────────────────────────────────────────────────

def create_user(email: str, full_name: str, password: str, role: str = "viewer") -> dict:
    """Create a new user. Returns the created user dict or raises ValueError."""
    conn = _get_conn()
    try:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            raise ValueError("Email đã được đăng ký")

        now = datetime.now(timezone.utc).isoformat()
        cur = conn.execute(
            "INSERT INTO users (email, full_name, hashed_password, role, is_active, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (email, full_name, hash_password(password), role, 1, now),
        )
        conn.commit()
        return get_user_by_id(cur.lastrowid)
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[dict]:
    """Look up user by email."""
    conn = _get_conn()
    try:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Look up user by ID."""
    conn = _get_conn()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_users() -> list[dict]:
    """Return all users (without hashed_password)."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT id, email, full_name, role, is_active, created_at, last_login "
            "FROM users ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_last_login(user_id: int):
    """Stamp last_login for the given user."""
    conn = _get_conn()
    try:
        now = datetime.now(timezone.utc).isoformat()
        conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, user_id))
        conn.commit()
    finally:
        conn.close()


def update_user_profile(user_id: int, full_name: Optional[str] = None, password: Optional[str] = None):
    """Update a user's profile fields."""
    conn = _get_conn()
    try:
        if full_name:
            conn.execute("UPDATE users SET full_name = ? WHERE id = ?", (full_name, user_id))
        if password:
            conn.execute(
                "UPDATE users SET hashed_password = ? WHERE id = ?",
                (hash_password(password), user_id),
            )
        conn.commit()
    finally:
        conn.close()


def update_user_role(user_id: int, role: str):
    """Change a user's role (admin/editor/viewer)."""
    conn = _get_conn()
    try:
        conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        conn.commit()
    finally:
        conn.close()


def deactivate_user(user_id: int):
    """Soft-delete: set is_active = 0."""
    conn = _get_conn()
    try:
        conn.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()


# ── Refresh token management ────────────────────────────────────────────────

def store_refresh_token(user_id: int, token: str, expires_at: str):
    """Store a refresh token in the DB."""
    conn = _get_conn()
    try:
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO refresh_tokens (user_id, token, expires_at, created_at) "
            "VALUES (?, ?, ?, ?)",
            (user_id, token, expires_at, now),
        )
        conn.commit()
    finally:
        conn.close()


def verify_refresh_token(token: str) -> Optional[dict]:
    """Verify a refresh token exists and is not expired.

    Returns the token row dict or None.
    """
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM refresh_tokens WHERE token = ?", (token,)
        ).fetchone()
        if not row:
            return None

        # Check expiry
        expires = datetime.fromisoformat(row["expires_at"])
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires:
            # Expired — clean up
            conn.execute("DELETE FROM refresh_tokens WHERE id = ?", (row["id"],))
            conn.commit()
            return None

        return dict(row)
    finally:
        conn.close()


def revoke_refresh_token(token: str):
    """Delete a refresh token (logout)."""
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM refresh_tokens WHERE token = ?", (token,))
        conn.commit()
    finally:
        conn.close()


def revoke_all_user_tokens(user_id: int):
    """Revoke all refresh tokens for a user."""
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM refresh_tokens WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()
