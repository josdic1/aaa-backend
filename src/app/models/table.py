# app/models/table.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.dining_room import DiningRoom
    from app.models.seat_assignment import SeatAssignment

class Table(Base):
    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(primary_key=True)

    dining_room_id: Mapped[int] = mapped_column(
        ForeignKey("dining_rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(80), nullable=False)

    # how many people can sit at this table
    seat_count: Mapped[int] = mapped_column(Integer, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    dining_room: Mapped["DiningRoom"] = relationship(
        "DiningRoom",
        back_populates="tables",
    )

    seat_assignments: Mapped[list["SeatAssignment"]] = relationship(
        "SeatAssignment",
        back_populates="table",
        cascade="all, delete-orphan",
    )   