# app/schemas/member.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class MemberBase(BaseModel):
    name: str = Field(..., max_length=120)
    relation: Optional[str] = Field(None, max_length=50)
    dietary_restrictions: Optional[List[str]] = None


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    relation: Optional[str] = Field(None, max_length=50)
    dietary_restrictions: Optional[List[str]] = None


class MemberRead(MemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime