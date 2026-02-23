# app/api/routes/orders.py
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, selectinload

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.models.seat_assignment import SeatAssignment  # Added Import
from app.models.table import Table                    # Added Import
from app.models.user import User
from app.schemas.orders import OrderEnsureRequest, OrderResponse, OrderUpdateRequest

router = APIRouter(prefix="/orders", tags=["orders"])


def _require_attendee_ownership(db: Session, user: User, attendee_id: int) -> ReservationAttendee:
    attendee = db.get(ReservationAttendee, attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
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

    _require_attendee_ownership(db, user, order.attendee_id)

    # Lifecycle lock: members cannot edit a fired or fulfilled order
    if order.status in ("fired", "fulfilled") and user.role not in ("admin", "staff"):
        raise HTTPException(status_code=409, detail="Order is locked")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(order, k, v)
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/fire", response_model=OrderResponse)
def fire_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = db.query(Order).options(
        selectinload(Order.items)
    ).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    _require_attendee_ownership(db, user, order.attendee_id)

    if order.status == "fired":
        raise HTTPException(status_code=400, detail="Order already fired")
    if order.status == "fulfilled":
        raise HTTPException(status_code=400, detail="Order already fulfilled")
    if not order.items:
        raise HTTPException(status_code=400, detail="Cannot fire an empty order")

    order.status = "fired"
    for item in order.items:
        if item.status == "selected":
            item.status = "confirmed"

    db.commit()
    db.refresh(order)
    return order


@router.get("/{order_id}/chit", response_class=HTMLResponse)
def get_chit(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Fixed Query: Added deep selectinload to reach the Room and Table name
    order = (
        db.query(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.attendee)
                .selectinload(ReservationAttendee.reservation)
                .selectinload(Reservation.seat_assignment)
                .selectinload(SeatAssignment.table)
                .selectinload(Table.dining_room),
            selectinload(Order.attendee)
                .selectinload(ReservationAttendee.member),
        )
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    attendee = order.attendee
    reservation = attendee.reservation

    # seat assignment logic
    seat_info = "Unassigned"
    if reservation.seat_assignment and reservation.seat_assignment.table:
        table = reservation.seat_assignment.table
        room = table.dining_room
        seat_info = f"{room.name} — {table.name}"

    # attendee name
    if attendee.member_id and attendee.member:
        name = attendee.member.name
    else:
        name = attendee.guest_name or "Guest"

    # dietary restrictions
    dietary = ", ".join(attendee.dietary_restrictions) if attendee.dietary_restrictions else "None"

    # items: Changed to include 'selected' so you can print before firing if needed
    items_html = ""
    for item in order.items:
        if item.status in ("selected", "confirmed"):
            items_html += f"""
            <tr>
                <td>{item.name_snapshot or "—"}</td>
                <td>{item.quantity}</td>
                <td>${(item.price_cents_snapshot or 0) / 100:.2f}</td>
            </tr>"""

    fired_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Chit #{order_id}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: monospace; font-size: 13px; padding: 24px; max-width: 400px; }}
  h1 {{ font-size: 18px; border-bottom: 2px solid #000; padding-bottom: 8px; margin-bottom: 12px; }}
  .meta {{ margin-bottom: 16px; line-height: 1.8; }}
  .meta strong {{ display: inline-block; width: 120px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
  th {{ text-align: left; border-bottom: 1px solid #000; padding: 4px 0; font-size: 11px; text-transform: uppercase; }}
  td {{ padding: 6px 0; border-bottom: 1px dotted #ccc; }}
  .footer {{ margin-top: 20px; font-size: 11px; color: #666; border-top: 1px solid #000; padding-top: 8px; }}
  @media print {{
    body {{ padding: 8px; }}
    button {{ display: none; }}
  }}
</style>
</head>
<body>
<h1>KITCHEN CHIT #{order_id}</h1>
<div class="meta">
  <div><strong>Guest:</strong> {name}</div>
  <div><strong>Table:</strong> {seat_info}</div>
  <div><strong>Date:</strong> {reservation.date}</div>
  <div><strong>Time:</strong> {reservation.start_time}</div>
  <div><strong>Dietary:</strong> {dietary}</div>
  <div><strong>Fired:</strong> {fired_at}</div>
</div>
<table>
  <thead><tr><th>Item</th><th>Qty</th><th>Price</th></tr></thead>
  <tbody>{items_html if items_html else "<tr><td colspan='3'>No items confirmed</td></tr>"}</tbody>
</table>
<div class="footer">Order #{order_id} — Abeyton Lodge</div>
<br>
<button onclick="window.print()">PRINT</button>
</body>
</html>"""

    return HTMLResponse(content=html)