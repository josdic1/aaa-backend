# app/schemas/orders.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attendee_id: int
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class OrderEnsureRequest(BaseModel):
    attendee_id: int = Field(..., ge=1)


class OrderUpdateRequest(BaseModel):
    status: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = Field(None, max_length=500)