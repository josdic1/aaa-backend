import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer

# Internal Imports
from app.core.config import get_settings
from app.api.routes import (
    auth, users, members, reservations, reservation_attendees,
    menu_items, orders, order_items, messages, dining_rooms,
    tables, seat_assignments, admin, schema, health
)

# ── 0. PATH CONFIGURATION ──
APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent.parent           # project root
TOOLS_DIR = APP_DIR / "tools" / "html"

settings = get_settings()
print(f"[CORS] ALLOWED_ORIGINS={settings.ALLOWED_ORIGINS}")
bearer_scheme = HTTPBearer(auto_error=False)

# --- JWT DEBUG (dev only): verify server is reading the env you expect ---
try:
    alg = getattr(settings, "JWT_ALGORITHM", None) or "HS256"

    # Source of truth: Settings field
    secret = getattr(settings, "JWT_SECRET_KEY", None)

    # Optional fallback (only for debugging env wiring)
    if not secret:
        secret = os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET")

    if secret:
        s = str(secret)
        print(f"[JWT] alg={alg} secret_present=True secret_len={len(s)}")
    else:
        print(f"[JWT] alg={alg} secret_present=False")
except Exception as e:
    print(f"[JWT] debug failed: {e}")

# ── 1. LIFESPAN ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    audit_api_routes(app)           # run audit at startup
    yield
    # shutdown logic can go here later (db pools, etc.)

app = FastAPI(lifespan=lifespan)

# ── 2. CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list(),
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["Authorization"],
    max_age=86400,
)

# ── 3. STATIC UTILS ──


# ── 4. ROUTER SYSTEM ──
API_PREFIX = "/api"

# Public / System
app.include_router(health.router,    prefix=API_PREFIX, tags=["Health"])
app.include_router(auth.router,      prefix=API_PREFIX, tags=["Auth"])
app.include_router(schema.router,    prefix=API_PREFIX, tags=["System"])

# Core
app.include_router(users.router,     prefix=API_PREFIX, tags=["Users"])
app.include_router(members.router,   prefix=API_PREFIX, tags=["Members"])

# Logistics
for router_mod in [reservations, reservation_attendees, menu_items,
                   dining_rooms, tables, seat_assignments]:
    app.include_router(router_mod.router, prefix=API_PREFIX, tags=["Logistics"])

# Business
app.include_router(orders.router,       prefix=API_PREFIX, tags=["Orders"])
app.include_router(order_items.router,  prefix=API_PREFIX, tags=["Orders"])
app.include_router(messages.router,     prefix=API_PREFIX, tags=["Messages"])
app.include_router(admin.router,        prefix=API_PREFIX, tags=["Admin"])

# ── 5. CUSTOM OPENAPI + SELECTIVE SECURITY ──
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AAA Backend API",
        version="1.0.0",
        description="API for AAA Backend Management System",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token"
        }
    }

    public_paths = {
        f"{API_PREFIX}/auth/login",
        f"{API_PREFIX}/auth/refresh",   # ← add if you have refresh endpoint
        f"{API_PREFIX}/health",
        f"{API_PREFIX}/health/",
    }

    for path, path_item in openapi_schema["paths"].items():
        if path in public_paths:
            continue
        for method in path_item.values():
            method.setdefault("security", []).append({"BearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ── 6. ROUTE AUDIT ──
def audit_api_routes(app_obj):
    print("\n🔍 ROUTE AUDIT: Checking for trailing slash inconsistencies...")
    api_paths = sorted(p for p in (r.path for r in app_obj.routes) if p and p.startswith(API_PREFIX))
    for p in api_paths:
        status = "✅ SLASH" if p.endswith("/") else "⚪ NAKED"
        print(f"   {status} → {p}")

