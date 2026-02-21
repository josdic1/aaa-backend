# app/api/routes/reservation_attendees.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps.db import get_db
from app.api.deps.auth import get_current_user
from app.models.user import User
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.schemas.reservation_attendee import (
    ReservationAttendeeCreate,
    ReservationAttendeeUpdate,
    ReservationAttendeeRead,
)

router = APIRouter(prefix="/reservation-attendees", tags=["reservation-attendees"])


def _ensure_owner(db: Session, reservation_id: int, user_id: int) -> None:
    r = db.get(Reservation, reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if r.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")


def _enum_list_to_str(values):
    if values is None:
        return None
    return [v.value for v in values]


@router.post("", response_model=ReservationAttendeeRead, status_code=status.HTTP_201_CREATED)
def create_attendee(
    payload: ReservationAttendeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_owner(db, payload.reservation_id, current_user.id)

    attendee = ReservationAttendee(
        reservation_id=payload.reservation_id,
        member_id=payload.member_id,
        guest_name=payload.guest_name,
        dietary_restrictions=_enum_list_to_str(payload.dietary_restrictions),
        meta=payload.meta,
        selection_confirmed=bool(payload.selection_confirmed) if payload.selection_confirmed is not None else False,
    )

    db.add(attendee)
    db.commit()
    db.refresh(attendee)
    return attendee


@router.get("/reservation/{reservation_id}", response_model=list[ReservationAttendeeRead])
def list_attendees(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_owner(db, reservation_id, current_user.id)

    stmt = (
        select(ReservationAttendee)
        .where(ReservationAttendee.reservation_id == reservation_id)
        .order_by(ReservationAttendee.id)
    )
    return db.execute(stmt).scalars().all()


@router.patch("/{attendee_id}", response_model=ReservationAttendeeRead)
def update_attendee(
    attendee_id: int,
    payload: ReservationAttendeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attendee = db.get(ReservationAttendee, attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")

    # verify ownership
    if attendee.reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Apply only allowed fields
    if payload.member_id is not None:
        attendee.member_id = payload.member_id
    if payload.guest_name is not None:
        attendee.guest_name = payload.guest_name
    if payload.dietary_restrictions is not None:
        # convert enums to strings
        attendee.dietary_restrictions = [v.value for v in payload.dietary_restrictions]
    if payload.meta is not None:
        attendee.meta = payload.meta
    if payload.selection_confirmed is not None:
        attendee.selection_confirmed = payload.selection_confirmed

    db.commit()
    db.refresh(attendee)
    return attendee


@router.delete("/{attendee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendee(
    attendee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attendee = db.get(ReservationAttendee, attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")

    _ensure_owner(db, attendee.reservation_id, current_user.id)

    db.delete(attendee)
    db.commit()
    return None