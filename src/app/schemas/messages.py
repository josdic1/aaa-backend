# app/schemas/messages.py
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MessageSender(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class MessageCreate(BaseModel):
    reservation_id: int
    body: str = Field(min_length=1)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reservation_id: int
    body: str
    created_at: datetime
    sender: MessageSender