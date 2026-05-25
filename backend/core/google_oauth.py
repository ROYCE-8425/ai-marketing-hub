"""
Google OAuth2 — Verify Google ID token and find/create user.

Flow:
1. Frontend uses Google Identity Services (GSI) to get ID token
2. Frontend sends token to POST /api/auth/google
3. This module verifies the token with Google's servers
4. If valid → find or create user → return JWT tokens
"""

from __future__ import annotations

import os
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")


async def verify_google_token(credential: str) -> Optional[dict]:
    """Verify a Google ID token by calling Google's tokeninfo endpoint.

    Returns dict with {email, name, picture, sub} on success, None on failure.
    Uses httpx instead of google-auth library to avoid heavy dependency.
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Google's tokeninfo endpoint verifies the token for us
            resp = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": credential}
            )

            if resp.status_code != 200:
                logger.warning("Google token verification failed: %s", resp.text)
                return None

            data = resp.json()

            # Verify audience matches our client ID
            if GOOGLE_CLIENT_ID and data.get("aud") != GOOGLE_CLIENT_ID:
                logger.warning("Google token audience mismatch: %s", data.get("aud"))
                return None

            # Verify email is verified
            if data.get("email_verified") != "true":
                logger.warning("Google email not verified: %s", data.get("email"))
                return None

            return {
                "email": data["email"],
                "name": data.get("name", data["email"].split("@")[0]),
                "picture": data.get("picture", ""),
                "google_id": data.get("sub", ""),
            }

    except Exception as e:
        logger.error("Google token verification error: %s", e)
        return None
