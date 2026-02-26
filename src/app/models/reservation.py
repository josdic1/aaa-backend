# app/models/reservation.py
from __future__ import annotations

from datetime import datetime, date, time, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Date, Time, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.reservation_attendee import ReservationAttendee
    from app.models.message import Message
    from app.models.seat_assignment import SeatAssignment
    from app.models.dining_room import DiningRoom


def _fmt_date(d: date | None) -> str:
    return d.strftime("%Y%m%d") if d else "00000000"


def _fmt_time(t: time | None) -> str:
    # "HHMM" 24-hour
    return t.strftime("%H%M") if t else "0000"


def _fmt_int(val: int | None, width: int) -> str:
    if val is None:
        return "0" * width
    return str(val).zfill(width)


def _make_reservation_code(res: "Reservation") -> str:
    # Example: ABY-20260224-1830-DR03-U0007-R0026
    # Keep this deterministic and derived from real fields.
    lodge = "ABY"
    d = _fmt_date(getattr(res, "date", None))
    st = _fmt_time(getattr(res, "start_time", None))
    dr = f"DR{_fmt_int(getattr(res, 'dining_room_id', None), 2)}"
    u = f"U{_fmt_int(getattr(res, 'user_id', None), 4)}"
    rid = f"R{_fmt_int(getattr(res, 'id', None), 4)}"
    return f"{lodge}-{d}-{st}-{dr}-{u}-{rid}"


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Room preference chosen by member at booking time
    dining_room_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("dining_rooms.id", ondelete="SET NULL"),
        nullable=True,
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

    # NEW: derived “coded data” string (stored)
    # Note: migration will add this as nullable first, then backfill, then set NOT NULL + unique if desired.
    reservation_code: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True,
        index=True,
        unique=True,
    )

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
    dining_room: Mapped[Optional["DiningRoom"]] = relationship("DiningRoom")

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


@event.listens_for(Reservation, "before_insert")
def _reservation_before_insert(mapper, connection, target: Reservation) -> None:
    # id may not exist yet; we’ll finalize after insert in the next step (migration/backfill).
    # Still set a provisional code so it’s never blank in memory.
    if not target.reservation_code:
        target.reservation_code = _make_reservation_code(target)


@event.listens_for(Reservation, "before_update")
def _reservation_before_update(mapper, connection, target: Reservation) -> None:
    # Keep it aligned with edited fields
    target.reservation_code = _make_reservation_code(target)