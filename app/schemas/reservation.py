# app/schemas/reservation.py
from __future__ import annotations

from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ReservationBase(BaseModel):
    date: date
    start_time: time
    end_time: Optional[time] = None
    status: Optional[str] = "draft"
    notes: Optional[str] = Field(None, max_length=500)


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ReservationRead(ReservationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime