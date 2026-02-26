# app/schemas/reservation.py
from __future__ import annotations

from datetime import date as dt_date
from datetime import datetime
from datetime import time as dt_time
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ReservationStatus = Literal["draft", "confirmed", "cancelled"]


class ReservationBase(BaseModel):
    date: dt_date
    start_time: dt_time
    end_time: Optional[dt_time] = None
    status: ReservationStatus = "draft"
    notes: Optional[str] = Field(None, max_length=500)
    dining_room_id: Optional[int] = None


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    date: Optional[dt_date] = None
    start_time: Optional[dt_time] = None
    end_time: Optional[dt_time] = None
    status: Optional[ReservationStatus] = None
    notes: Optional[str] = None
    dining_room_id: Optional[int] = None


class ReservationRead(ReservationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime