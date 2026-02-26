from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.reservation_attendee import ReservationAttendee

DIETARY_RESTRICTIONS = [
    "dairy_free", "egg_free", "fish_allergy", "gluten_free",
    "halal", "kosher", "nut_allergy", "peanut_allergy",
    "sesame_allergy", "shellfish_allergy", "soy_free",
    "vegan", "vegetarian",
]

dietary_enum = ENUM(
    *DIETARY_RESTRICTIONS,
    name="dietary_restriction_enum",
    create_type=False,
)

class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)

    relation: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        server_default="Primary",
    )

    dietary_restrictions: Mapped[List[str]] = mapped_column(
        ARRAY(dietary_enum),
        nullable=False,
        server_default=text("'{}'::dietary_restriction_enum[]"),
    )

    # --- Timestamps Fixed & Nested ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("TIMEZONE('utc', now())"), 
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(
        "User",
        back_populates="members",
    )

    reservation_attendees: Mapped[List["ReservationAttendee"]] = relationship(
        "ReservationAttendee",
        back_populates="member",
    )

    def __repr__(self) -> str:
        return f"<Member(id={self.id}, name={self.name!r}, relation={self.relation!r})>"