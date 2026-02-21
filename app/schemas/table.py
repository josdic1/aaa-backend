# app/schemas/table.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TableBase(BaseModel):
    name: str
    dining_room_id: int
    seat_count: int
    is_active: Optional[bool] = True


class TableCreate(TableBase):
    pass


class TableUpdate(BaseModel):
    name: Optional[str] = None
    seat_count: Optional[int] = None
    is_active: Optional[bool] = None


class TableRead(TableBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime