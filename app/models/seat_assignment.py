# app/models/seat_assignment.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.table import Table
    from app.models.user import User


class SeatAssignment(Base):
    __tablename__ = "seat_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    table_id: Mapped[int] = mapped_column(
        ForeignKey("tables.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    assigned_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    reservation: Mapped["Reservation"] = relationship(
        "Reservation", back_populates="seat_assignment"
    )
    table: Mapped["Table"] = relationship(
        "Table", back_populates="seat_assignments"
    )
    assigned_by: Mapped[Optional["User"]] = relationship("User")