# app/models/revoked_token.py
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    __table_args__ = (
        Index("ix_revoked_tokens_jti", "jti", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # JWT ID (unique per token)
    jti: Mapped[str] = mapped_column(String(36), nullable=False)

    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )