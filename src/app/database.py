from __future__ import annotations

from typing import Generator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()


# ── 1. Naming Conventions for clean, readable migrations ──
POSTGRES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)


# ── 2. Engine with production-friendly pooling ──
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,         # detect & recover broken connections
    pool_size=10,               # persistent connections
    max_overflow=20,            # allow bursts (e.g. dinner rush)
    pool_timeout=30,            # wait time before raising error
    pool_recycle=1800,          # recycle after ~30 min to avoid stale connections
    echo=settings.ENV == "dev", # show SQL in development only
)


# ── 3. Session factory ──
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,     # better performance & prevents detached instance issues
)


# ── 4. Dependency (use this in FastAPI routes) ──
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency: yields a DB session and ensures it's closed afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()