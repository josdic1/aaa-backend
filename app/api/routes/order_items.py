# app/api/routes/order_items.py
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.menu_item import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.reservation_attendee import ReservationAttendee
from app.models.user import User
from app.schemas.order_items import OrderItemCreateRequest, OrderItemResponse, OrderItemUpdateRequest

router = APIRouter(prefix="/order-items", tags=["order_items"])


def _require_order_access(db: Session, user: User, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    attendee = db.get(ReservationAttendee, order.attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")

    if attendee.reservation.user_id != user.id and user.role not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Not allowed")

    return order


@router.get("/by-order/{order_id}", response_model=List[OrderItemResponse])
def list_items_for_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _require_order_access(db, user, order_id)

    return (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order_id)
        .order_by(OrderItem.id.asc())
        .all()
    )


@router.post("/by-order/{order_id}", response_model=OrderItemResponse)
def add_item_to_order(
    order_id: int,
    payload: OrderItemCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _require_order_access(db, user, order_id)

    menu_item = db.get(MenuItem, payload.menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    item = OrderItem(
        order_id=order_id,
        menu_item_id=payload.menu_item_id,
        quantity=payload.quantity,
        status=payload.status,
        meta=payload.meta,
        # history snapshots
        name_snapshot=menu_item.name,
        price_cents_snapshot=menu_item.price_cents,
    )

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{order_item_id}", response_model=OrderItemResponse)
def update_order_item(
    order_item_id: int,
    payload: OrderItemUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = db.get(OrderItem, order_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order item not found")

    _require_order_access(db, user, item.order_id)

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(item, k, v)

    db.commit()
    db.refresh(item)
    return item