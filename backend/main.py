from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import json

from routers import api_seo
from routers import api_content
from routers import api_execution
from routers import api_data
from routers import api_polish
from routers import api_serp
from routers import api_new_features
from routers import api_phase2
from routers import api_phase3
from routers import api_convert
from routers import api_auth
from routers import api_user_auth
from routers import api_satellite
from routers import api_seo_tools
from routers import api_content_writer

app = FastAPI(
    title="AI Marketing Hub — Backend",
    version="3.2.0",
    description=(
        "AI Marketing Hub API — Phase 20: SEO Audit, CRO, Competitor Gap, "
        "Content Planning, Publish, Opportunity Scoring, Live Data Connectors, "
        "Content Polish, Live SERP, Dashboard, Rank Tracker, Spin Editor, "
        "GEO Optimizer, Backlinks, Content Calendar, Technical SEO, "
        "AI Reports, Multi-site, A/B Testing, File Converter, Usage History"
    ),
)


# ── Usage History Middleware ─────────────────────────────────────────────────

class UsageHistoryMiddleware(BaseHTTPMiddleware):
    """Auto-log all API requests and responses."""

    SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip non-API and static paths
        if path in self.SKIP_PATHS or not path.startswith("/api"):
            return await call_next(request)

        start = time.time()
        input_data = None
        error_msg = None

        # Capture request body
        try:
            body = await request.body()
            if body:
                input_data = json.loads(body)
        except Exception:
            input_data = None

        # Execute request
        try:
            response = await call_next(request)
            status = response.status_code

            # Capture response body
            output_data = None
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk if isinstance(chunk, bytes) else chunk.encode()

            try:
                output_data = json.loads(response_body)
            except Exception:
                output_data = response_body[:500].decode("utf-8", errors="replace") if response_body else None

            duration = (time.time() - start) * 1000

            # Log to usage history
            try:
                from core.usage_history import log_usage
                log_usage(
                    endpoint=path,
                    method=request.method,
                    input_data=input_data,
                    output_data=output_data,
                    status_code=status,
                    duration_ms=duration,
                    error=error_msg,
                )
            except Exception:
                pass  # Don't fail request due to logging

            # Return new response with captured body
            return Response(
                content=response_body,
                status_code=status,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        except Exception as e:
            duration = (time.time() - start) * 1000
            error_msg = str(e)
            try:
                from core.usage_history import log_usage
                log_usage(
                    endpoint=path,
                    method=request.method,
                    input_data=input_data,
                    output_data=None,
                    status_code=500,
                    duration_ms=duration,
                    error=error_msg,
                )
            except Exception:
                pass
            raise


app.add_middleware(UsageHistoryMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_seo.router)
app.include_router(api_content.router)
app.include_router(api_execution.router)
app.include_router(api_data.router)
app.include_router(api_polish.router)
app.include_router(api_serp.router)
app.include_router(api_new_features.router)
app.include_router(api_phase2.router)
app.include_router(api_phase3.router)
app.include_router(api_convert.router)
app.include_router(api_auth.router)
app.include_router(api_user_auth.router)
app.include_router(api_satellite.router)
app.include_router(api_seo_tools.router)
app.include_router(api_content_writer.router)


@app.on_event("startup")
async def auto_setup():
    """Auto-add default site and sync rank tracker on startup if empty."""
    import os
    try:
        from core.site_manager import get_sites, add_site, set_active_site
        sites = get_sites()
        if not sites:
            site_url = os.getenv("GSC_SITE_URL", "https://binhphuocmitsubishi.com/")
            result = add_site(
                name="Mitsubishi Bình Phước",
                url=site_url,
                description="Đại lý chính hãng Mitsubishi tại Bình Phước",
                niche="ô tô",
            )
            if result.get("id"):
                set_active_site(result["id"])
    except Exception:
        pass  # Non-critical — site can be added manually


@app.get("/health")
async def health():
    return {"status": "ok", "phase": 20, "version": "3.2.0"}


@app.get("/api/server-config")
async def server_config():
    """Return server-side API key status (masked) for the config page."""
    import os
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)

    def _mask(val: str) -> dict:
        """Return {configured: bool, masked: str} for a key value."""
        if not val:
            return {"configured": False, "masked": ""}
        if len(val) <= 8:
            return {"configured": True, "masked": val[:2] + "***"}
        return {"configured": True, "masked": val[:6] + "..." + val[-4:]}

    groq = os.getenv("GROQ_API_KEY", "")
    psi = os.getenv("PAGESPEED_API_KEY", "")
    ga4_prop = os.getenv("GA4_PROPERTY_ID", "")
    ga4_refresh = os.getenv("GA4_REFRESH_TOKEN", "") or os.getenv("GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN", "")
    gsc_client = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
    gsc_secret = os.getenv("GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET", "")
    gsc_refresh = os.getenv("GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN", "")
    gsc_site = os.getenv("GSC_SITE_URL", "")
    dfs_login = os.getenv("DATAFORSEO_LOGIN", "")
    dfs_pass = os.getenv("DATAFORSEO_PASSWORD", "")
    jwt_secret = os.getenv("JWT_SECRET_KEY", "")

    return {
        "groq_api_key": _mask(groq),
        "pagespeed_api_key": _mask(psi),
        "ga4_property_id": _mask(ga4_prop),
        "ga4_refresh_token": _mask(ga4_refresh),
        "gsc_client_id": _mask(gsc_client),
        "gsc_client_secret": _mask(gsc_secret),
        "gsc_refresh_token": _mask(gsc_refresh),
        "gsc_site_url": {"configured": bool(gsc_site), "masked": gsc_site},
        "dataforseo_login": _mask(dfs_login),
        "dataforseo_password": _mask(dfs_pass),
        "jwt_secret_key": _mask(jwt_secret),
    }


@app.post("/api/server-config")
async def update_server_config(request: Request):
    """Update API keys in the backend .env file."""
    import os
    from dotenv import load_dotenv

    body = await request.json()
    env_path = os.path.join(os.path.dirname(__file__), ".env")

    # Map of allowed frontend keys → .env variable names
    KEY_MAP = {
        "groq_api_key": "GROQ_API_KEY",
        "pagespeed_api_key": "PAGESPEED_API_KEY",
        "ga4_property_id": "GA4_PROPERTY_ID",
        "gsc_client_id": "GOOGLE_SEARCH_CONSOLE_CLIENT_ID",
        "gsc_client_secret": "GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET",
        "gsc_refresh_token": "GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN",
        "gsc_site_url": "GSC_SITE_URL",
        "dataforseo_login": "DATAFORSEO_LOGIN",
        "dataforseo_password": "DATAFORSEO_PASSWORD",
        "jwt_secret_key": "JWT_SECRET_KEY",
    }

    updates = {}
    for frontend_key, env_key in KEY_MAP.items():
        if frontend_key in body and body[frontend_key]:
            updates[env_key] = body[frontend_key]

    if not updates:
        return {"status": "error", "message": "Không có giá trị nào để cập nhật."}

    # Read existing .env, update or append keys
    lines: list[str] = []
    seen: set[str] = set()
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                stripped = line.strip()
                if "=" in stripped and not stripped.startswith("#"):
                    key = stripped.split("=", 1)[0]
                    if key in updates:
                        lines.append(f"{key}={updates[key]}\n")
                        seen.add(key)
                    else:
                        lines.append(line if line.endswith("\n") else line + "\n")
                else:
                    lines.append(line if line.endswith("\n") else line + "\n")

    for key, val in updates.items():
        if key not in seen:
            lines.append(f"{key}={val}\n")

    with open(env_path, "w") as f:
        f.writelines(lines)

    load_dotenv(env_path, override=True)
    return {"status": "ok", "message": f"Đã cập nhật {len(updates)} key(s).", "updated": list(updates.keys())}


# ── Usage History API ────────────────────────────────────────────────────────

@app.get("/api/usage-history")
async def get_history(limit: int = 50, endpoint: str = None):
    """Lịch sử sử dụng — xem toàn bộ API calls."""
    from core.usage_history import get_usage_history
    return get_usage_history(limit=limit, endpoint_filter=endpoint)


@app.get("/api/usage-stats")
async def get_stats():
    """Thống kê sử dụng — tổng calls, success rate, errors."""
    from core.usage_history import get_usage_stats
    return get_usage_stats()


@app.delete("/api/usage-history")
async def clear_usage_history():
    """Xóa lịch sử sử dụng."""
    from core.usage_history import clear_history
    clear_history()
    return {"status": "ok", "message": "Đã xóa lịch sử"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
