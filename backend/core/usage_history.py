"""
Usage History Logger — Middleware ghi lại toàn bộ input/output API calls
(Upgraded to SQLAlchemy)

Tự động log:
- Endpoint called
- Input (request body)
- Output (response body, truncated)
- Status code
- Duration
- Errors
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from core.database import SessionLocal
from core.models import UsageLog

def _truncate(obj: Any, max_len: int = 500) -> str:
    """Truncate large values for storage and convert to string."""
    if isinstance(obj, str):
        return obj[:max_len] + "..." if len(obj) > max_len else obj
    if isinstance(obj, (dict, list)):
        try:
            s = json.dumps(obj, ensure_ascii=False)
            return s[:max_len] + "..." if len(s) > max_len else s
        except Exception:
            s = str(obj)
            return s[:max_len] + "..." if len(s) > max_len else s
    s = str(obj)
    return s[:max_len] + "..." if len(s) > max_len else s


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
    db = SessionLocal()
    try:
        log_entry = UsageLog(
            endpoint=endpoint,
            method=method,
            input_data=_truncate(input_data),
            output_data=_truncate(output_data),
            status_code=status_code,
            duration_ms=round(duration_ms, 1),
            error=error
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        return {
            "id": log_entry.id,
            "timestamp": log_entry.created_at.isoformat() if log_entry.created_at else None,
            "endpoint": log_entry.endpoint,
            "method": log_entry.method,
            "input": log_entry.input_data,
            "output": log_entry.output_data,
            "status_code": log_entry.status_code,
            "duration_ms": log_entry.duration_ms,
            "error": log_entry.error,
            "success": status_code < 400 and not error,
        }
    finally:
        db.close()


def get_usage_history(limit: int = 50, endpoint_filter: str = None) -> List[Dict[str, Any]]:
    """Get usage history, optionally filtered by endpoint."""
    db = SessionLocal()
    try:
        query = db.query(UsageLog)
        if endpoint_filter:
            query = query.filter(UsageLog.endpoint.like(f"%{endpoint_filter}%"))
            
        logs = query.order_by(UsageLog.created_at.desc()).limit(limit).all()
        return [{
            "id": l.id,
            "timestamp": l.created_at.isoformat() if l.created_at else None,
            "endpoint": l.endpoint,
            "method": l.method,
            "input": l.input_data,
            "output": l.output_data,
            "status_code": l.status_code,
            "duration_ms": l.duration_ms,
            "error": l.error,
            "success": l.status_code < 400 and not l.error,
        } for l in logs]
    finally:
        db.close()


def get_usage_stats() -> Dict[str, Any]:
    """Get usage statistics summary."""
    db = SessionLocal()
    try:
        total = db.query(UsageLog).count()
        if total == 0:
            return {"total_calls": 0, "success_rate": 0, "endpoints": {}}

        # For SQLite/PostgreSQL compatibility, we do aggregation in Python or simple queries
        logs = db.query(UsageLog).all()
        success = 0
        endpoints = {}
        last_call = None
        
        for l in logs:
            if l.status_code < 400 and not l.error:
                success += 1
                
            ep = l.endpoint
            if ep not in endpoints:
                endpoints[ep] = {"calls": 0, "success": 0, "errors": 0, "avg_ms": 0.0}
                
            endpoints[ep]["calls"] += 1
            if l.status_code < 400 and not l.error:
                endpoints[ep]["success"] += 1
            else:
                endpoints[ep]["errors"] += 1
                
            endpoints[ep]["avg_ms"] = (
                endpoints[ep]["avg_ms"] * (endpoints[ep]["calls"] - 1) + l.duration_ms
            ) / endpoints[ep]["calls"]
            
            if not last_call or (l.created_at and last_call < l.created_at):
                last_call = l.created_at
                
        errors = total - success

        for ep in endpoints:
            endpoints[ep]["avg_ms"] = round(endpoints[ep]["avg_ms"], 1)

        return {
            "total_calls": total,
            "success": success,
            "errors": errors,
            "success_rate": round(success / max(total, 1) * 100, 1),
            "endpoints": endpoints,
            "last_call": last_call.isoformat() if last_call else None,
        }
    finally:
        db.close()


def clear_history():
    """Clear all usage history."""
    db = SessionLocal()
    try:
        db.query(UsageLog).delete()
        db.commit()
    finally:
        db.close()
