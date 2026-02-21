# app/schemas/seat_assignment.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SeatAssignmentCreate(BaseModel):
    reservation_id: int
    table_id: int
    notes: Optional[str] = None


class SeatAssignmentUpdate(BaseModel):
    table_id: Optional[int] = None
    notes: Optional[str] = None


class SeatAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reservation_id: int
    table_id: int
    assigned_by_user_id: Optional[int] = None
    assigned_at: datetime
    notes: Optional[str] = None