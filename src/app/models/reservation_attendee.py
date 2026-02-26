from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional, Dict, Any

from sqlalchemy import ForeignKey, String, DateTime, JSON, Boolean, text
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.member import Member
    from app.models.order import Order


DIETARY_RESTRICTIONS = [
    "dairy_free", "egg_free", "fish_allergy", "gluten_free",
    "halal", "kosher", "nut_allergy", "peanut_allergy",
    "sesame_allergy", "shellfish_allergy", "soy_free",
    "vegan", "vegetarian",
]

dietary_enum = ENUM(
    *DIETARY_RESTRICTIONS,
    name="dietary_restriction_enum",
    create_type=True,  # Alembic creates enum if missing
)


class ReservationAttendee(Base):
    __tablename__ = "reservation_attendees"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    member_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    guest_name: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True,
    )

    dietary_restrictions: Mapped[List[str]] = mapped_column(
        ARRAY(dietary_enum),
        nullable=False,
        server_default=text("'{}'::dietary_restriction_enum[]"),
    )

    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        default=None,
    )

    selection_confirmed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )

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

    reservation: Mapped["Reservation"] = relationship(
        "Reservation",
        back_populates="attendees",
    )

    member: Mapped[Optional["Member"]] = relationship(
        "Member",
        back_populates="reservation_attendees",  # add this relationship on Member side if needed
    )

    order: Mapped[Optional["Order"]] = relationship(
        "Order",
        back_populates="attendee",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        name = self.guest_name or f"Member {self.member_id}"
        return f"<ReservationAttendee(id={self.id}, name={name!r}, confirmed={self.selection_confirmed})>"