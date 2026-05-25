"""
API User Auth Router — JWT email/password authentication.

Separate from api_auth.py (Google OAuth).

Endpoints:
  POST /api/auth/register         — Register new user
  POST /api/auth/login             — Login → {access_token, refresh_token, user}
  POST /api/auth/refresh           — Refresh access token
  POST /api/auth/logout            — Revoke refresh token
  GET  /api/auth/me                — Get current user profile
  PUT  /api/auth/me                — Update profile (full_name, password)
  GET  /api/auth/users             — List all users (admin only)
  PUT  /api/auth/users/{id}/role   — Change user role (admin only)
  DELETE /api/auth/users/{id}      — Deactivate user (admin only)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.auth import (
    MessageResponse,
    RefreshRequest,
    RoleUpdate,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    require_admin,
    verify_password,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from core.auth_db import (
    create_user,
    deactivate_user,
    get_all_users,
    get_user_by_email,
    get_user_by_id,
    revoke_refresh_token,
    store_refresh_token,
    update_last_login,
    update_user_profile,
    update_user_role,
    verify_refresh_token,
)

router = APIRouter(prefix="/api/auth", tags=["Auth — User JWT"])


# ── Helpers ──────────────────────────────────────────────────────────────────

def _user_to_response(user: dict) -> UserResponse:
    """Convert a DB user dict to a UserResponse model."""
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        is_active=bool(user["is_active"]),
        created_at=user["created_at"],
        last_login=user.get("last_login"),
    )


def _generate_tokens(user: dict) -> TokenResponse:
    """Create access + refresh tokens and persist refresh token."""
    token_data = {"sub": str(user["id"]), "email": user["email"], "role": user["role"]}

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Store refresh token in DB
    expires_at = (
        datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    ).isoformat()
    store_refresh_token(user["id"], refresh_token, expires_at)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=_user_to_response(user),
    )


# ── POST /api/auth/register ─────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate):
    """Register a new user account."""
    try:
        user = create_user(
            email=body.email.strip().lower(),
            full_name=body.full_name.strip(),
            password=body.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    update_last_login(user["id"])

    # Send welcome email in background (non-blocking)
    import asyncio
    async def _send():
        from core.email_service import send_welcome_email
        await asyncio.to_thread(send_welcome_email, user["email"], user["full_name"])
    asyncio.create_task(_send())

    return _generate_tokens(user)


# ── POST /api/auth/google ───────────────────────────────────────────────────

class GoogleAuthRequest(BaseModel):
    credential: str

@router.post("/google", response_model=TokenResponse)
async def google_auth(body: GoogleAuthRequest):
    """Authenticate or register user via Google OAuth.

    Receives a Google ID token from the frontend GSI flow.
    Verifies the token, then:
      - If user exists → login
      - If user doesn't exist → auto-register → login
    """
    from core.google_oauth import verify_google_token
    from core.auth_db import create_google_user

    google_data = await verify_google_token(body.credential)
    if not google_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Google không hợp lệ hoặc đã hết hạn",
        )

    email = google_data["email"].lower()
    name = google_data["name"]

    # Check if user already exists
    user = get_user_by_email(email)

    if not user:
        # Auto-register new Google user
        try:
            user = create_google_user(email=email, full_name=name)
        except ValueError:
            # Race condition: user was created between check and insert
            user = get_user_by_email(email)

    if not user or not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa",
        )

    update_last_login(user["id"])
    return _generate_tokens(user)


# ── POST /api/auth/login ────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin):
    """Authenticate user with email + password."""
    user = get_user_by_email(body.email.strip().lower())
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng",
        )
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa",
        )

    update_last_login(user["id"])
    return _generate_tokens(user)


# ── POST /api/auth/refresh ──────────────────────────────────────────────────

@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest):
    """Exchange a valid refresh token for a new access + refresh pair."""
    # Verify refresh token exists in DB
    stored = verify_refresh_token(body.refresh_token)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ hoặc đã hết hạn",
        )

    # Decode JWT to get user info
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise Exception("Not a refresh token")
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ",
        )

    user = get_user_by_id(user_id)
    if not user or not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị vô hiệu hóa",
        )

    # Revoke old refresh token (rotation)
    revoke_refresh_token(body.refresh_token)

    return _generate_tokens(user)


# ── POST /api/auth/logout ───────────────────────────────────────────────────

@router.post("/logout", response_model=MessageResponse)
async def logout(body: RefreshRequest):
    """Revoke the given refresh token."""
    revoke_refresh_token(body.refresh_token)
    return MessageResponse(message="Đã đăng xuất thành công")


# ── GET /api/auth/me ─────────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return _user_to_response(user)


# ── PUT /api/auth/me ─────────────────────────────────────────────────────────

@router.put("/me", response_model=UserResponse)
async def update_me(body: UserUpdate, user: dict = Depends(get_current_user)):
    """Update the current user's profile (full_name, password)."""
    update_user_profile(
        user_id=user["id"],
        full_name=body.full_name,
        password=body.password,
    )
    updated = get_user_by_id(user["id"])
    return _user_to_response(updated)


# ── GET /api/auth/users ─────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserResponse])
async def list_users(admin: dict = Depends(require_admin)):
    """List all users (admin only)."""
    users = get_all_users()
    return [_user_to_response(u) for u in users]


# ── PUT /api/auth/users/{id}/role ────────────────────────────────────────────

@router.put("/users/{user_id}/role", response_model=UserResponse)
async def change_role(user_id: int, body: RoleUpdate, admin: dict = Depends(require_admin)):
    """Change a user's role (admin only)."""
    target = get_user_by_id(user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    if target["id"] == admin["id"]:
        raise HTTPException(status_code=400, detail="Không thể thay đổi vai trò của chính mình")

    update_user_role(user_id, body.role)
    updated = get_user_by_id(user_id)
    return _user_to_response(updated)


# ── DELETE /api/auth/users/{id} ──────────────────────────────────────────────

@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: int, admin: dict = Depends(require_admin)):
    """Deactivate a user (admin only). Does not permanently delete."""
    target = get_user_by_id(user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    if target["id"] == admin["id"]:
        raise HTTPException(status_code=400, detail="Không thể vô hiệu hóa chính mình")

    deactivate_user(user_id)
    return MessageResponse(message=f"Đã vô hiệu hóa tài khoản {target['email']}")
