# app/api/routes/members.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps.db import get_db
from app.api.deps.auth import get_current_user
from app.models.member import Member
from app.models.user import User
from app.schemas.member import MemberCreate, MemberRead, MemberUpdate

router = APIRouter(prefix="/members", tags=["members"])


# Create Member
@router.post("", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def create_member(
    payload: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = Member(
        user_id=current_user.id,
        name=payload.name,
        relation=payload.relation,
        dietary_restrictions=payload.dietary_restrictions,
    )

    db.add(member)
    db.commit()
    db.refresh(member)
    return member


# List My Members
@router.get("", response_model=list[MemberRead])
def list_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Member).where(Member.user_id == current_user.id).order_by(Member.id)
    return db.execute(stmt).scalars().all()


# Get One
@router.get("/{member_id}", response_model=MemberRead)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = db.get(Member, member_id)

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return member


# Update
@router.put("/{member_id}", response_model=MemberRead)
def update_member(
    member_id: int,
    payload: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = db.get(Member, member_id)

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    if payload.name is not None:
        member.name = payload.name

    if payload.relation is not None:
        member.relation = payload.relation

    if payload.dietary_restrictions is not None:
        member.dietary_restrictions = payload.dietary_restrictions

    db.commit()
    db.refresh(member)
    return member


# Delete
@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = db.get(Member, member_id)

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(member)
    db.commit()
    return None