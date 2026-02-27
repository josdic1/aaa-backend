# app/api/routes/health.py
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.core.config import get_settings

# Reuse your existing auth dependency (optional token)
from app.api.deps.auth import get_current_user_optional

settings = get_settings()

router = APIRouter(prefix="/health", tags=["System"])


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("")
def health(
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
):
    started = time.perf_counter()

    db_ok = True
    db_error: Optional[str] = None
    db_latency_ms: Optional[int] = None

    # Database ping (cheap + reliable)
    try:
        t0 = time.perf_counter()
        db.execute(text("SELECT 1"))
        db_latency_ms = int((time.perf_counter() - t0) * 1000)
    except Exception as e:  # pragma: no cover (varies by driver/env)
        db_ok = False
        db_error = str(e)

    elapsed_ms = int((time.perf_counter() - started) * 1000)

     # Optional auth check:
    # - If Authorization: Bearer <token> is present, we validate it and report ok/fail.
    # - If no token is present, we report skipped (endpoint stays monitoring-friendly).
    auth_header = request.headers.get("authorization") or ""
    has_bearer = auth_header.lower().startswith("bearer ")

    if not has_bearer:
        auth_check = {
            "status": "skipped",
            "note": "No bearer token provided.",
        }
    elif user is None:
        auth_check = {
            "status": "fail",
            "note": "Bearer token provided but invalid/expired.",
        }
    else:
        auth_check = {
            "status": "ok",
            "note": "Bearer token validated.",
            "user_id": getattr(user, "id", None),
            "role": getattr(user, "role", None),
        }

    payload: Dict[str, Any] = {
        "status": "ok" if db_ok else "degraded",
        "service": "aaa-backend",
        "env": settings.ENV,
        "time_utc": utc_now_iso(),
        "latency_ms": elapsed_ms,
        "checks": {
            "server": {"status": "ok"},
            "database": {
                "status": "ok" if db_ok else "fail",
                "latency_ms": db_latency_ms,
                "error": db_error,
            },
            "auth": auth_check,
        },
    }

    status_code = 200 if db_ok else 503
    return JSONResponse(payload, status_code=status_code)

@router.get("/debug/alembic")
def debug_alembic(db: Session = Depends(get_db)):
    # 1) Alembic version table (may not exist)
    try:
        current = db.execute(text("SELECT version_num FROM alembic_version")).fetchall()
        current = [r[0] for r in current]
    except Exception as e:
        current = {"error": str(e)}

    # 2) Public tables list
    try:
        tables = db.execute(
            text(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname='public'
                ORDER BY tablename;
                """
            )
        ).fetchall()
        tables = [r[0] for r in tables]
    except Exception as e:
        tables = {"error": str(e)}

    return {"alembic_version": current, "tables": tables}