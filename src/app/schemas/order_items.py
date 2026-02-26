# app/schemas/order_items.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    menu_item_id: int
    quantity: int
    status: str
    name_snapshot: Optional[str] = None
    price_cents_snapshot: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class OrderItemCreateRequest(BaseModel):
    menu_item_id: int = Field(..., ge=1)
    quantity: int = Field(1, ge=1)
    status: str = Field("selected", max_length=20)
    meta: Optional[Dict[str, Any]] = None


class OrderItemUpdateRequest(BaseModel):
    quantity: Optional[int] = Field(None, ge=1)
    status: Optional[str] = Field(None, max_length=20)
    meta: Optional[Dict[str, Any]] = None