# app/api/routes/menu_items.py
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.menu_item import MenuItem
from app.models.user import User
from app.schemas.menu_item import MenuItemCreate, MenuItemResponse, MenuItemUpdate


router = APIRouter(prefix="/menu-items", tags=["menu_items"])


def require_admin(user: User) -> None:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )


@router.get("", response_model=List[MenuItemResponse])
def list_menu_items(
    include_inactive: bool = Query(False, description="Include inactive menu items (admin/staff use)"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(MenuItem)
    if not include_inactive or user.role != "admin":
        q = q.filter(MenuItem.is_active.is_(True))
    return q.order_by(MenuItem.name.asc()).all()


@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    payload: MenuItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_admin(user)

    item = MenuItem(
        name=payload.name,
        description=payload.description,
        price_cents=payload.price_cents,
        dietary_restrictions=payload.dietary_restrictions,
        is_active=payload.is_active,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{menu_item_id}", response_model=MenuItemResponse)
def update_menu_item(
    menu_item_id: int,
    payload: MenuItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_admin(user)

    item = db.get(MenuItem, menu_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(item, k, v)

    db.commit()
    db.refresh(item)
    return item