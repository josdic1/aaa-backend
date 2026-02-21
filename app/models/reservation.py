# app/models/reservation.py
from __future__ import annotations

from datetime import datetime, date, time, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Date, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.reservation_attendee import ReservationAttendee
    from app.models.message import Message
    from app.models.seat_assignment import SeatAssignment


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
        server_default="draft",
        index=True,
    )

    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship("User")

    attendees: Mapped[List["ReservationAttendee"]] = relationship(
        "ReservationAttendee",
        back_populates="reservation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="reservation",
        cascade="all, delete-orphan",
    )

    seat_assignment: Mapped[Optional["SeatAssignment"]] = relationship(
        "SeatAssignment",
        back_populates="reservation",
        cascade="all, delete-orphan",
        uselist=False,
    )