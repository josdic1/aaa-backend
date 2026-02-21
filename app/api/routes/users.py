from typing import List
from functools import partial

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.api.deps.auth import hash_password, get_current_user
from app.api.deps.permissions import require_permission
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

# Create partial dependencies to inject entity/action
get_user_read_scope = partial(require_permission, entity="users", action="read")
get_user_write_scope = partial(require_permission, entity="users", action="write")
get_user_delete_scope = partial(require_permission, entity="users", action="delete")


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    response: Response,
    db: Session = Depends(get_db),
    scope: str = Depends(get_user_write_scope),
):
    # Only admins can create users
    if scope != "all":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create users",
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role or "member",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")
    db.refresh(user)

    response.headers["Location"] = f"/api/users/{user.id}"
    return user


@router.get("", response_model=List[UserRead])
def list_users(
    db: Session = Depends(get_db),
    scope: str = Depends(get_user_read_scope),
    current_user: User = Depends(get_current_user),
):
    if scope == "all":
        return db.execute(select(User).order_by(User.id)).scalars().all()
    else:  # member can only see self
        return [current_user]


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    scope: str = Depends(get_user_read_scope),
    current_user: User = Depends(get_current_user),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if scope == "own" and user.id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this user")

    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    scope: str = Depends(get_user_write_scope),
    current_user: User = Depends(get_current_user),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Members can only update self and cannot change role
    if scope == "own" and user.id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this user")
    if scope == "own" and payload.role is not None:
        raise HTTPException(status_code=403, detail="Members cannot update role")

    # Apply updates
    if payload.email is not None:
        user.email = payload.email
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)
    if payload.role is not None:
        user.role = payload.role  # Only admin can reach here

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")

    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    scope: str = Depends(get_user_delete_scope),
    current_user: User = Depends(get_current_user),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="You do not have permission to delete users")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return None