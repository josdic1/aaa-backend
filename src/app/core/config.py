from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict
# add near your imports

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    STAFF_INVITE_CODE: str = Field(
    default="",
    description="Required code to register as staff",
    )

    # ── ENVIRONMENT ──
    ENV: str = Field(
        default="dev",
        pattern=r"^(dev|prod|test)$",
        description="Environment: dev, prod or test",
    )
    PORT: int = Field(default=8080, ge=1, le=65535)

    # ── CORS ──
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        description="Comma-separated list of allowed origins",
    )

    # ── DATABASE ──
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/aaa",
        description="PostgreSQL connection string",
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_postgres_protocol(cls, v: str) -> str:
        if isinstance(v, str):
            # Railway/Heroku often provide 'postgres://'
            # We need 'postgresql+psycopg://' for SQLAlchemy 2 + psycopg3
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+psycopg://", 1)
            elif v.startswith("postgresql://") and "+psycopg" not in v:
                v = v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v

    # ── JWT ──
    # Canonical secret used by the server.
    # Accept either env var name: JWT_SECRET_KEY (preferred) OR JWT_SECRET (legacy)

    JWT_SECRET_KEY: str = Field(
        default="change-me-in-production-very-important",
        validation_alias=AliasChoices("JWT_SECRET_KEY", "JWT_SECRET"),
        description="JWT signing secret (accepts JWT_SECRET_KEY or JWT_SECRET)",
)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    def origins_list(self) -> List[str]:
        if not self.ALLOWED_ORIGINS:
            return []
        return [
            o.strip()
            for o in self.ALLOWED_ORIGINS.split(",")
            if o.strip() and o.strip().lower() != "null"
        ]

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def secret_must_be_strong(cls, v: str, info) -> str:
        if info.data.get("ENV") == "prod" and v in {
            "change-me-in-production-very-important",
            "dev-secret",
            "secret",
            "",
        }:
            raise ValueError(
                "JWT_SECRET_KEY must be a strong, unique value in production "
                "(not 'dev-secret', 'secret', or the default placeholder)"
            )
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()