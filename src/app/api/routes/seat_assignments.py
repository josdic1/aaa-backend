from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.reservation import Reservation
from app.models.seat_assignment import SeatAssignment
from app.models.user import User
from app.schemas.seat_assignment import (
    SeatAssignmentCreate,
    SeatAssignmentRead,
    SeatAssignmentUpdate,
)

router = APIRouter(prefix="/seat-assignments", tags=["seat_assignments"])


def _require_staff(user: User) -> None:
    if getattr(user, "role", None) not in ("staff", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff only")


def _reservation_window(reservation: Reservation) -> tuple[datetime, datetime]:
    """
    Build start_at/end_at for seat assignment from Reservation date + times.

    If end_time is NULL, default to +90 minutes (must stay consistent with migration backfill).
    """
    start_at = datetime.combine(reservation.date, reservation.start_time)

    if reservation.end_time:
        end_at = datetime.combine(reservation.date, reservation.end_time)
    else:
        end_at = start_at + timedelta(minutes=90)

    if end_at <= start_at:
        raise HTTPException(
            status_code=400,
            detail="Reservation end time must be after start time",
        )

    return start_at, end_at


@router.get("/{reservation_id}", response_model=SeatAssignmentRead)
def get_assignment(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assignment = (
        db.query(SeatAssignment)
        .filter(SeatAssignment.reservation_id == reservation_id)
        .first()
    )
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="No seat assignment for this reservation",
        )
    return assignment


@router.post("", response_model=SeatAssignmentRead, status_code=status.HTTP_201_CREATED)
def create_assignment(
    payload: SeatAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_staff(current_user)

    existing = (
        db.query(SeatAssignment)
        .filter(SeatAssignment.reservation_id == payload.reservation_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Reservation already has a table assigned. Use PATCH to update.",
        )

    reservation = db.get(Reservation, payload.reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    start_at, end_at = _reservation_window(reservation)

    assignment = SeatAssignment(
        reservation_id=payload.reservation_id,
        table_id=payload.table_id,
        assigned_by_user_id=current_user.id,
        notes=payload.notes,
        start_at=start_at,
        end_at=end_at,
    )

    db.add(assignment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Covers: EXCLUDE overlap violations and other integrity issues
        raise HTTPException(
            status_code=409,
            detail="This table is already assigned during that time window.",
        )

    db.refresh(assignment)
    return assignment


@router.patch("/{assignment_id}", response_model=SeatAssignmentRead)
def update_assignment(
    assignment_id: int,
    payload: SeatAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_staff(current_user)

    assignment = db.get(SeatAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    data = payload.model_dump(exclude_unset=True)

    # If table_id is being changed, keep the same reservation window.
    # If you later allow changing reservation times after assignment,
    # you must also update start_at/end_at here or via a separate endpoint.
    if "table_id" in data:
        reservation = db.get(Reservation, assignment.reservation_id)
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")
        start_at, end_at = _reservation_window(reservation)
        assignment.start_at = start_at
        assignment.end_at = end_at

    for k, v in data.items():
        setattr(assignment, k, v)

    assignment.assigned_by_user_id = current_user.id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This table is already assigned during that time window.",
        )

    db.refresh(assignment)
    return assignment


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_staff(current_user)

    assignment = db.get(SeatAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    db.delete(assignment)
    db.commit()
    return None