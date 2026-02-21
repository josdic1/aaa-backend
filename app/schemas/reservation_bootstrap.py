# app/schemas/reservation_bootstrap.py
from __future__ import annotations

from typing import List, Dict
from pydantic import BaseModel, ConfigDict

from app.schemas.reservation import ReservationRead
from app.schemas.reservation_attendee import ReservationAttendeeRead
from app.schemas.orders import OrderResponse
from app.schemas.order_items import OrderItemResponse
from app.schemas.messages import MessageResponse


class ReservationBootstrapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reservation: ReservationRead
    party_size: int
    attendees: List[ReservationAttendeeRead]
    orders: List[OrderResponse]
    order_items: List[OrderItemResponse]
    order_totals: Dict[int, int]
    reservation_total: int
    messages: List[MessageResponse]