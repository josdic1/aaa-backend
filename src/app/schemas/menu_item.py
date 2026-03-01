# app/schemas/menu_item.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MenuItemBase(BaseModel):
    name: str = Field(..., max_length=140)
    description: Optional[str] = Field(None, max_length=500)
    price_cents: int = Field(..., ge=0)
    category: Optional[str] = Field(None, max_length=60)
    dietary_restrictions: List[str] = Field(default_factory=list)
    is_active: bool = True


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    # All optional for PATCH-style update
    name: Optional[str] = Field(None, max_length=140)
    description: Optional[str] = Field(None, max_length=500)
    price_cents: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=60)
    dietary_restrictions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class MenuItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    price_cents: int
    category: Optional[str] = None
    dietary_restrictions: List[str] = Field(default_factory=list)
    is_active: bool
    created_at: datetime
    updated_at: datetime