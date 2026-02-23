# app/api/routes/dining_rooms.py
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.models.dining_room import DiningRoom
from app.schemas import DiningRoomCreate, DiningRoomRead
from app.api.deps.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dining-rooms", tags=["dining_rooms"])


def _require_admin(user: User) -> None:
    if getattr(user, "role", None) != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")


@router.get("/", response_model=List[DiningRoomRead])
def list_dining_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # authenticated users can view active rooms
    rooms = db.query(DiningRoom).filter(DiningRoom.is_active.is_(True)).order_by(DiningRoom.name).all()
    return rooms


@router.post("/", response_model=DiningRoomRead, status_code=status.HTTP_201_CREATED)
def create_dining_room(
    payload: DiningRoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)

    existing = db.query(DiningRoom).filter(DiningRoom.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Dining room with this name already exists")

    room = DiningRoom(
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room