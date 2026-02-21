# app/api/routes/reservations.py
from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.order import Order
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.models.user import User
from app.schemas.reservation import ReservationCreate, ReservationRead, ReservationUpdate
from app.schemas.reservation_bootstrap import ReservationBootstrapResponse

router = APIRouter(prefix="/reservations", tags=["reservations"])


# ── LIST ──────────────────────────────────────────────────
@router.get("", response_model=List[ReservationRead])
def list_reservations(
    status: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Reservation).filter(Reservation.user_id == current_user.id)

    if status:
        q = q.filter(Reservation.status == status)
    if from_date:
        q = q.filter(Reservation.date >= from_date)
    if to_date:
        q = q.filter(Reservation.date <= to_date)

    return q.order_by(Reservation.date.asc(), Reservation.start_time.asc()).all()


# ── CREATE ────────────────────────────────────────────────
@router.post("", response_model=ReservationRead, status_code=201)
def create_reservation(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = Reservation(
        user_id=current_user.id,
        date=payload.date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        status=payload.status or "draft",
        notes=payload.notes,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


# ── GET ───────────────────────────────────────────────────
@router.get("/{reservation_id}", response_model=ReservationRead)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return reservation


# ── UPDATE ────────────────────────────────────────────────
@router.patch("/{reservation_id}", response_model=ReservationRead)
def update_reservation(
    reservation_id: int,
    payload: ReservationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(reservation, k, v)

    db.commit()
    db.refresh(reservation)
    return reservation


# ── DELETE ────────────────────────────────────────────────
@router.delete("/{reservation_id}", status_code=204)
def delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(reservation)
    db.commit()
    return None


# ── BOOTSTRAP ─────────────────────────────────────────────
@router.get("/{reservation_id}/bootstrap", response_model=ReservationBootstrapResponse)
def get_reservation_bootstrap(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = (
        db.query(Reservation)
        .options(
            selectinload(Reservation.attendees)
            .selectinload(ReservationAttendee.order)
            .selectinload(Order.items),
            selectinload(Reservation.messages),
        )
        .filter(Reservation.id == reservation_id)
        .first()
    )

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # ensure every attendee has an order
    created = False
    for attendee in reservation.attendees:
        if attendee.order is None:
            new_order = Order(attendee_id=attendee.id, status="open")
            db.add(new_order)
            created = True

    if created:
        db.commit()
        db.refresh(reservation)

    attendees = reservation.attendees
    orders = [a.order for a in attendees if a.order]
    order_items = [item for o in orders for item in o.items]
    messages = reservation.messages

    party_size = len(attendees)
    order_totals = {}
    reservation_total = 0

    for order in orders:
        total = 0
        for item in order.items:
            if item.status != "selected":
                continue
            if item.price_cents_snapshot is None:
                continue
            if item.quantity is None:
                continue
            total += item.price_cents_snapshot * item.quantity

        order_totals[order.id] = total
        reservation_total += total

    return {
        "reservation": reservation,
        "party_size": party_size,
        "attendees": attendees,
        "orders": orders,
        "order_items": order_items,
        "order_totals": order_totals,
        "reservation_total": reservation_total,
        "messages": messages,
    }