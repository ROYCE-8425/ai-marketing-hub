"""
Usage History Logger — Middleware ghi lại toàn bộ input/output API calls

Tự động log:
- Endpoint called
- Input (request body)
- Output (response body, truncated)
- Status code
- Duration
- Errors
"""

import os
import json
import time
from datetime import datetime
from typing import Any, Dict, List

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "usage_history.json")
MAX_HISTORY = 500  # Keep last 500 entries


def _ensure_dir():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)


def _load_history() -> List[Dict[str, Any]]:
    _ensure_dir()
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_history(history: List[Dict[str, Any]]):
    _ensure_dir()
    # Keep only last MAX_HISTORY entries
    history = history[-MAX_HISTORY:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def _truncate(obj: Any, max_len: int = 500) -> Any:
    """Truncate large values for storage."""
    if isinstance(obj, str):
        return obj[:max_len] + "..." if len(obj) > max_len else obj
    if isinstance(obj, dict):
        return {k: _truncate(v, max_len) for k, v in list(obj.items())[:20]}
    if isinstance(obj, list):
        return [_truncate(v, max_len) for v in obj[:10]]
    return obj


def log_usage(
    endpoint: str,
    method: str,
    input_data: Any,
    output_data: Any,
    status_code: int,
    duration_ms: float,
    error: str = None,
):
    """Log a single API usage entry."""
    history = _load_history()
    entry = {
        "id": len(history) + 1,
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "method": method,
        "input": _truncate(input_data),
        "output": _truncate(output_data),
        "status_code": status_code,
        "duration_ms": round(duration_ms, 1),
        "error": error,
        "success": status_code < 400 and not error,
    }
    history.append(entry)
    _save_history(history)
    return entry


def get_usage_history(limit: int = 50, endpoint_filter: str = None) -> List[Dict[str, Any]]:
    """Get usage history, optionally filtered by endpoint."""
    history = _load_history()
    if endpoint_filter:
        history = [h for h in history if endpoint_filter in h.get("endpoint", "")]
    return list(reversed(history[-limit:]))


def get_usage_stats() -> Dict[str, Any]:
    """Get usage statistics summary."""
    history = _load_history()
    if not history:
        return {"total_calls": 0, "success_rate": 0, "endpoints": {}}

    total = len(history)
    success = sum(1 for h in history if h.get("success"))
    errors = total - success

    # Group by endpoint
    endpoints = {}
    for h in history:
        ep = h.get("endpoint", "unknown")
        if ep not in endpoints:
            endpoints[ep] = {"calls": 0, "success": 0, "errors": 0, "avg_ms": 0}
        endpoints[ep]["calls"] += 1
        if h.get("success"):
            endpoints[ep]["success"] += 1
        else:
            endpoints[ep]["errors"] += 1
        endpoints[ep]["avg_ms"] = (
            endpoints[ep]["avg_ms"] * (endpoints[ep]["calls"] - 1) + h.get("duration_ms", 0)
        ) / endpoints[ep]["calls"]

    # Round avg_ms
    for ep in endpoints:
        endpoints[ep]["avg_ms"] = round(endpoints[ep]["avg_ms"], 1)

    return {
        "total_calls": total,
        "success": success,
        "errors": errors,
        "success_rate": round(success / max(total, 1) * 100, 1),
        "endpoints": endpoints,
        "last_call": history[-1].get("timestamp") if history else None,
    }


def clear_history():
    """Clear all usage history."""
    _save_history([])
