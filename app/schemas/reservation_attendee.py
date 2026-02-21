# app/schemas/reservation_attendee.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, model_validator


class DietaryRestriction(str, Enum):
    dairy_free = "dairy_free"
    egg_free = "egg_free"
    fish_allergy = "fish_allergy"
    gluten_free = "gluten_free"
    halal = "halal"
    kosher = "kosher"
    nut_allergy = "nut_allergy"
    peanut_allergy = "peanut_allergy"
    sesame_allergy = "sesame_allergy"
    shellfish_allergy = "shellfish_allergy"
    soy_free = "soy_free"
    vegan = "vegan"
    vegetarian = "vegetarian"


class ReservationAttendeeBase(BaseModel):
    member_id: Optional[int] = None
    guest_name: Optional[str] = Field(None, max_length=120)
    dietary_restrictions: Optional[List[DietaryRestriction]] = None
    meta: Optional[Dict[str, Any]] = None
    selection_confirmed: Optional[bool] = None


class ReservationAttendeeCreate(ReservationAttendeeBase):
    reservation_id: int

    @model_validator(mode="after")
    def require_identity(self):
        guest = (self.guest_name or "").strip()
        if self.member_id is None and guest == "":
            raise ValueError("member_id or guest_name is required")
        self.guest_name = guest or None
        return self


class ReservationAttendeeUpdate(BaseModel):
    member_id: Optional[int] = None
    guest_name: Optional[str] = Field(None, max_length=120)
    dietary_restrictions: Optional[List[DietaryRestriction]] = None
    meta: Optional[Dict[str, Any]] = None
    selection_confirmed: Optional[bool] = None


class ReservationAttendeeRead(ReservationAttendeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reservation_id: int
    created_at: datetime
    updated_at: datetime