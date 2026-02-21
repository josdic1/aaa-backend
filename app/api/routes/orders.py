# app/api/routes/orders.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.order import Order
from app.models.reservation_attendee import ReservationAttendee
from app.models.user import User
from app.schemas.orders import OrderEnsureRequest, OrderResponse, OrderUpdateRequest

router = APIRouter(prefix="/orders", tags=["orders"])


def _require_attendee_ownership(db: Session, user: User, attendee_id: int) -> ReservationAttendee:
    attendee = db.get(ReservationAttendee, attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")

    # Ownership: attendee -> reservation -> user_id
    if attendee.reservation.user_id != user.id and user.role not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Not allowed")

    return attendee


@router.post("/ensure", response_model=OrderResponse)
def ensure_order(
    payload: OrderEnsureRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    attendee = _require_attendee_ownership(db, user, payload.attendee_id)

    if attendee.order:
        return attendee.order

    order = Order(attendee_id=attendee.id, status="open")
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    payload: OrderUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    attendee = _require_attendee_ownership(db, user, order.attendee_id)

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(order, k, v)

    db.commit()
    db.refresh(order)
    return order