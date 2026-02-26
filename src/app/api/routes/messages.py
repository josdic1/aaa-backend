# app/api/routes/messages.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.models.message import Message
from app.models.reservation import Reservation
from app.schemas.messages import MessageCreate, MessageResponse
from app.api.deps.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/messages", tags=["messages"])


# -----------------------------------------------------------
# List messages for a reservation
# -----------------------------------------------------------
@router.get("/by-reservation/{reservation_id}", response_model=list[MessageResponse])
def list_messages(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    messages = (
        db.query(Message)
        .filter(Message.reservation_id == reservation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return messages


# -----------------------------------------------------------
# Post message to reservation
# -----------------------------------------------------------
@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = db.get(Reservation, payload.reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    message = Message(
        reservation_id=payload.reservation_id,
        sender_user_id=current_user.id,
        body=payload.body,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message