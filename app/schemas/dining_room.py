# app/schemas/dining_room.py
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DiningRoomBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class DiningRoomCreate(DiningRoomBase):
    pass


class DiningRoomRead(DiningRoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime