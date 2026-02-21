# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse

from app.core.config import get_settings
from app.api.routes.users import router as users_router
from app.api.routes import auth
from app.api.routes import members
from app.api.routes import reservations
from app.api.routes import reservation_attendees
from app.api.routes import menu_items
from app.api.routes import orders
from app.api.routes import order_items
from app.api.routes import messages
from app.api.routes import dining_rooms
from app.api.routes import tables
from app.api.routes import seat_assignments

settings = get_settings()

bearer_scheme = HTTPBearer(auto_error=False)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/curl-gen", include_in_schema=False)
def curl_gen():
    return FileResponse("curl-gen.html")

@app.get("/db-viewer", include_in_schema=False)
def db_viewer():
    return FileResponse("db-viewer.html")


# Routers
app.include_router(auth.router)
app.include_router(users_router, prefix="/api")
app.include_router(members.router, prefix="/api")
app.include_router(reservations.router, prefix="/api")
app.include_router(reservation_attendees.router, prefix="/api")
app.include_router(menu_items.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(order_items.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(dining_rooms.router, prefix="/api")
app.include_router(tables.router, prefix="/api")
app.include_router(seat_assignments.router, prefix="/api")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AAA Backend API",
        version="1.0",
        description="API for AAA Backend",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"BearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi