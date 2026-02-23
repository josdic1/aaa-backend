# app/models/user.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, TYPE_CHECKING

from sqlalchemy import DateTime, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.member import Member


class User(Base):
    __tablename__ = "users"
    ### there is no name field in the user ##
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")

    # Role + optional per-user permissions
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="member",
        server_default="member",
        index=True,
    )

    # NOTE: This field is stored but not yet read by any permission logic.
    # Future use: per-user overrides on top of role-based access.   
    permissions: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        default=None,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # REQUIRED for Member.user back_populates="members"
    members: Mapped[List["Member"]] = relationship(
        "Member",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

