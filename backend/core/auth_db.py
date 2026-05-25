"""
Auth database — SQLAlchemy storage for users & refresh tokens.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from core.auth import hash_password
from core.database import SessionLocal
from core.models import User, RefreshToken

# ── User CRUD ────────────────────────────────────────────────────────────────

def create_user(email: str, full_name: str, password: str, role: str = "viewer") -> dict:
    """Create a new user. Returns the created user dict or raises ValueError."""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError("Email đã được đăng ký")

        new_user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=role,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return get_user_by_id(new_user.id)
    finally:
        db.close()


def create_google_user(email: str, full_name: str) -> dict:
    """Create a new user from Google OAuth (no password needed).

    Returns the created user dict or raises ValueError if email taken.
    """
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError("Email đã được đăng ký")

        new_user = User(
            email=email,
            full_name=full_name,
            hashed_password="GOOGLE_OAUTH",  # Marker: no password login
            role="viewer",
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return get_user_by_id(new_user.id)
    finally:
        db.close()

def get_user_by_email(email: str) -> Optional[dict]:
    """Look up user by email."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": user.hashed_password,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    finally:
        db.close()


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Look up user by ID."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": user.hashed_password,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    finally:
        db.close()


def get_all_users() -> list[dict]:
    """Return all users (without hashed_password)."""
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.created_at.desc()).all()
        return [{
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "last_login": u.last_login.isoformat() if u.last_login else None
        } for u in users]
    finally:
        db.close()


def update_last_login(user_id: int):
    """Stamp last_login for the given user."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()


def update_user_profile(user_id: int, full_name: Optional[str] = None, password: Optional[str] = None):
    """Update a user's profile fields."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            if full_name:
                user.full_name = full_name
            if password:
                user.hashed_password = hash_password(password)
            db.commit()
    finally:
        db.close()


def update_user_role(user_id: int, role: str):
    """Change a user's role (admin/editor/viewer)."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.role = role
            db.commit()
    finally:
        db.close()


def deactivate_user(user_id: int):
    """Soft-delete: set is_active = False."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            db.commit()
    finally:
        db.close()


# ── Refresh token management ────────────────────────────────────────────────

def store_refresh_token(user_id: int, token: str, expires_at: str):
    """Store a refresh token in the DB."""
    db = SessionLocal()
    try:
        exp_dt = datetime.fromisoformat(expires_at)
        new_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=exp_dt
        )
        db.add(new_token)
        db.commit()
    finally:
        db.close()


def verify_refresh_token(token: str) -> Optional[dict]:
    """Verify a refresh token exists and is not expired.

    Returns the token row dict or None.
    """
    db = SessionLocal()
    try:
        rt = db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if not rt:
            return None

        # Check expiry
        expires = rt.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires:
            # Expired — clean up
            db.delete(rt)
            db.commit()
            return None

        return {
            "id": rt.id,
            "user_id": rt.user_id,
            "token": rt.token,
            "expires_at": rt.expires_at.isoformat(),
            "created_at": rt.created_at.isoformat() if rt.created_at else None
        }
    finally:
        db.close()


def revoke_refresh_token(token: str):
    """Delete a refresh token (logout)."""
    db = SessionLocal()
    try:
        rt = db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if rt:
            db.delete(rt)
            db.commit()
    finally:
        db.close()


def revoke_all_user_tokens(user_id: int):
    """Revoke all refresh tokens for a user."""
    db = SessionLocal()
    try:
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        db.commit()
    finally:
        db.close()
