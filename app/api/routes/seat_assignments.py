# app/api/routes/seat_assignments.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.seat_assignment import SeatAssignment
from app.models.user import User
from app.schemas.seat_assignment import SeatAssignmentCreate, SeatAssignmentRead, SeatAssignmentUpdate

router = APIRouter(prefix="/seat-assignments", tags=["seat_assignments"])


def _require_staff(user: User) -> None:
    if getattr(user, "role", None) not in ("staff", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff only")


@router.get("/{reservation_id}", response_model=SeatAssignmentRead)
def get_assignment(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assignment = db.query(SeatAssignment).filter(
        SeatAssignment.reservation_id == reservation_id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="No seat assignment for this reservation")
    return assignment


@router.post("", response_model=SeatAssignmentRead, status_code=status.HTTP_201_CREATED)
def create_assignment(
    payload: SeatAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_staff(current_user)

    existing = db.query(SeatAssignment).filter(
        SeatAssignment.reservation_id == payload.reservation_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Reservation already has a table assigned. Use PATCH to update.")

    assignment = SeatAssignment(
        reservation_id=payload.reservation_id,
        table_id=payload.table_id,
        assigned_by_user_id=current_user.id,
        notes=payload.notes,
    )
    db.add(assignment)
    db.commit()
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
    for k, v in data.items():
        setattr(assignment, k, v)

    assignment.assigned_by_user_id = current_user.id

    db.commit()
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
