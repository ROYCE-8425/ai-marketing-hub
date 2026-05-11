"""
API Auth Router — Google OAuth2 1-click flow

Endpoints:
  GET  /auth/google/setup     — Returns auth_url for GSC + GA4 OAuth2 consent
  GET  /auth/google/callback  — Exchanges code for refresh_token, saves to .env

Scopes requested:
  - https://www.googleapis.com/auth/webmasters.readonly (GSC)
  - https://www.googleapis.com/auth/analytics.readonly (GA4)

This replaces the need for manual refresh_token setup.
"""

from __future__ import annotations

import os
import urllib.parse
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

# Load .env from backend root
_ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(_ENV_PATH)

router = APIRouter(tags=["Auth — Google OAuth2"])

# Scopes for both GSC and GA4
OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/analytics.readonly",
]

# Configurable redirect URI (default: local dev)
_DEFAULT_REDIRECT_URI = "http://localhost:8000/auth/google/callback"


def _get_redirect_uri() -> str:
    """Get redirect URI from env or use default."""
    return os.getenv("GOOGLE_OAUTH_REDIRECT_URI", _DEFAULT_REDIRECT_URI)


# ─────────────────────────────────────────────────────────────────────────────
# GET /auth/google/setup — Generate OAuth2 authorization URL
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/auth/google/setup")
async def google_auth_setup():
    """
    Generate Google OAuth2 authorization URL.

    Returns:
      - auth_url: URL to open in browser for user consent
      - scopes: list of requested scopes
      - redirect_uri: the callback URL that Google will redirect to

    Requires GOOGLE_SEARCH_CONSOLE_CLIENT_ID in .env.
    """
    load_dotenv(_ENV_PATH, override=True)
    client_id = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
    if not client_id:
        return {
            "error": "GOOGLE_SEARCH_CONSOLE_CLIENT_ID chưa được cấu hình trong .env",
            "source": "missing_credentials",
            "setup_instructions": (
                "1. Vào Google Cloud Console → APIs & Services → Credentials\n"
                "2. Tạo OAuth 2.0 Client ID (type: Web application)\n"
                "3. Thêm redirect URI: http://localhost:8000/auth/google/callback\n"
                "4. Copy Client ID và Client Secret vào backend/.env"
            ),
        }

    redirect_uri = _get_redirect_uri()
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(OAUTH_SCOPES),
        "access_type": "offline",
        "prompt": "consent",  # Force consent to always get refresh_token
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return {
        "auth_url": auth_url,
        "scopes": OAUTH_SCOPES,
        "redirect_uri": redirect_uri,
        "message": "Mở auth_url trong trình duyệt để cấp quyền Google Analytics + Search Console",
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /auth/google/callback — Exchange code for refresh_token
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/auth/google/callback")
async def google_auth_callback(code: str = Query(None), error: str = Query(None)):
    """
    OAuth2 callback: exchange authorization code for refresh_token.

    - Saves refresh_token to .env as GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN
    - Uses read-modify-write to preserve other env vars
    - Reloads env vars in current process
    - Returns success HTML page
    """
    if error:
        return HTMLResponse(f"""
        <html><head><title>OAuth Error</title></head>
        <body style="font-family:system-ui;background:#0f172a;color:#e2e8f0;display:flex;justify-content:center;align-items:center;height:100vh">
        <div style="text-align:center;max-width:500px">
            <h1 style="color:#fca5a5">❌ Lỗi xác thực</h1>
            <p>{error}</p>
            <a href="http://localhost:5173/" style="color:#c4b5fd;text-decoration:underline">← Quay về Dashboard</a>
        </div>
        </body></html>
        """, status_code=400)

    if not code:
        return HTMLResponse("""
        <html><head><title>OAuth Error</title></head>
        <body style="font-family:system-ui;background:#0f172a;color:#e2e8f0;display:flex;justify-content:center;align-items:center;height:100vh">
        <div style="text-align:center;max-width:500px">
            <h1 style="color:#fca5a5">❌ Không nhận được mã xác thực</h1>
            <p>Google không trả về authorization code.</p>
            <a href="http://localhost:5173/" style="color:#c4b5fd;text-decoration:underline">← Quay về Dashboard</a>
        </div>
        </body></html>
        """, status_code=400)

    load_dotenv(_ENV_PATH, override=True)
    client_id = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        return HTMLResponse("""
        <html><head><title>Config Error</title></head>
        <body style="font-family:system-ui;background:#0f172a;color:#e2e8f0;display:flex;justify-content:center;align-items:center;height:100vh">
        <div style="text-align:center;max-width:500px">
            <h1 style="color:#fca5a5">❌ Thiếu Client ID / Secret</h1>
            <p>Cần cấu hình GOOGLE_SEARCH_CONSOLE_CLIENT_ID và GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET trong .env</p>
            <a href="http://localhost:5173/" style="color:#c4b5fd;text-decoration:underline">← Quay về Dashboard</a>
        </div>
        </body></html>
        """, status_code=500)

    # Exchange authorization code for tokens
    redirect_uri = _get_redirect_uri()
    try:
        token_resp = httpx.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }, timeout=15.0)
        token_data = token_resp.json()
    except Exception as exc:
        return HTMLResponse(f"""
        <html><head><title>Token Error</title></head>
        <body style="font-family:system-ui;background:#0f172a;color:#e2e8f0;display:flex;justify-content:center;align-items:center;height:100vh">
        <div style="text-align:center;max-width:500px">
            <h1 style="color:#fca5a5">❌ Lỗi trao đổi token</h1>
            <p>{str(exc)[:200]}</p>
            <a href="http://localhost:5173/" style="color:#c4b5fd;text-decoration:underline">← Quay về Dashboard</a>
        </div>
        </body></html>
        """, status_code=500)

    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        error_detail = token_data.get("error_description", token_data.get("error", "Unknown"))
        return HTMLResponse(f"""
        <html><head><title>Token Error</title></head>
        <body style="font-family:system-ui;background:#0f172a;color:#e2e8f0;display:flex;justify-content:center;align-items:center;height:100vh">
        <div style="text-align:center;max-width:500px">
            <h1 style="color:#fca5a5">❌ Không nhận được refresh token</h1>
            <p>{error_detail}</p>
            <p style="color:#94a3b8;font-size:13px">Thử xóa quyền truy cập tại
            <a href="https://myaccount.google.com/permissions" target="_blank" style="color:#a5b4fc">myaccount.google.com/permissions</a>
            rồi thử lại.</p>
            <a href="http://localhost:5173/" style="color:#c4b5fd;text-decoration:underline">← Quay về Dashboard</a>
        </div>
        </body></html>
        """, status_code=400)

    # Save refresh token to .env using read-modify-write pattern
    _save_refresh_token_to_env(refresh_token)

    # Determine which scopes were granted
    granted_scopes = token_data.get("scope", "").split(" ")
    has_ga4 = "https://www.googleapis.com/auth/analytics.readonly" in granted_scopes
    has_gsc = "https://www.googleapis.com/auth/webmasters.readonly" in granted_scopes

    scope_status = []
    if has_gsc:
        scope_status.append("✅ Google Search Console")
    if has_ga4:
        scope_status.append("✅ Google Analytics 4")
    if not scope_status:
        scope_status.append("⚠️ Scopes không rõ (token vẫn có thể hoạt động)")

    scope_html = "<br>".join(scope_status)
    token_preview = f"{refresh_token[:20]}...{refresh_token[-10:]}"

    return HTMLResponse(f"""
    <html>
    <head><title>OAuth Thành Công</title></head>
    <body style="font-family:system-ui;background:#0f172a;color:#e2e8f0;display:flex;justify-content:center;align-items:center;height:100vh;margin:0">
    <div style="text-align:center;max-width:500px;padding:40px;background:rgba(30,41,59,0.8);border-radius:16px;border:1px solid rgba(99,102,241,0.3)">
        <div style="font-size:48px;margin-bottom:16px">🎉</div>
        <h1 style="color:#6ee7b7;margin:0 0 12px">Kết nối thành công!</h1>
        <div style="background:rgba(16,185,129,0.1);padding:12px;border-radius:8px;margin:16px 0;text-align:left;font-size:14px">
            {scope_html}
        </div>
        <p style="color:#94a3b8;font-size:13px">Token: <code style="color:#a5b4fc">{token_preview}</code></p>
        <p style="color:#cbd5e1">Refresh token đã được lưu vào .env.<br>GA4 và GSC đã sẵn sàng.</p>
        <a href="http://localhost:5173/"
           style="display:inline-block;margin-top:16px;padding:10px 24px;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;border-radius:8px;text-decoration:none;font-weight:500">
            ← Quay về Dashboard
        </a>
    </div>
    <script>
        // Notify opener window that auth is complete
        if (window.opener) {{
            window.opener.postMessage({{ type: 'google-oauth-complete', scopes: {granted_scopes} }}, '*');
        }}
    </script>
    </body>
    </html>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# GET /auth/google/status — Check current OAuth2 status
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/auth/google/status")
async def google_auth_status():
    """Check if OAuth2 credentials are configured and valid."""
    load_dotenv(_ENV_PATH, override=True)
    client_id = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET", "")
    refresh_token = os.getenv("GA4_REFRESH_TOKEN", "") or os.getenv("GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN", "")
    ga4_property = os.getenv("GA4_PROPERTY_ID", "")

    has_credentials = bool(client_id and client_secret)
    has_refresh_token = bool(refresh_token)
    has_ga4 = bool(ga4_property)

    if has_credentials and has_refresh_token:
        status = "connected"
    elif has_credentials:
        status = "needs_authorization"
    else:
        status = "not_configured"

    return {
        "status": status,
        "has_client_credentials": has_credentials,
        "has_refresh_token": has_refresh_token,
        "has_ga4_property_id": has_ga4,
        "ga4_property_id": ga4_property if has_ga4 else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Save refresh token to .env (read-modify-write)
# ─────────────────────────────────────────────────────────────────────────────

def _save_refresh_token_to_env(refresh_token: str):
    """Save refresh token to .env, preserving other keys."""
    env_lines = []
    found = False
    if os.path.exists(_ENV_PATH):
        with open(_ENV_PATH, "r") as f:
            for line in f:
                if line.startswith("GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN="):
                    env_lines.append(f"GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN={refresh_token}\n")
                    found = True
                else:
                    env_lines.append(line)
    if not found:
        env_lines.append(f"GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN={refresh_token}\n")

    with open(_ENV_PATH, "w") as f:
        f.writelines(env_lines)

    # Reload env vars in current process
    load_dotenv(_ENV_PATH, override=True)
