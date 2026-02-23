# app/api/routes/auth.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from app.api.deps.db import get_db
from app.api.deps.auth import (
    verify_password,
    create_access_token,
    get_current_user,
    hash_password,
    oauth2_scheme,
)
from app.core.config import get_settings
from app.models.revoked_token import RevokedToken
from app.models.user import User

settings = get_settings()

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Invite codes → role mapping
# Change STAFF2026 to whatever you want to hand out to staff
INVITE_CODES: dict[str, str] = {
    "STAFF2026": "staff",
}


# --- Schemas ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    invite_code: Optional[str] = None  # blank = member, valid code = staff (or whatever)


class RefreshRequest(BaseModel):
    refresh_token: str


# --- Endpoints ---

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Public registration.
    - No invite code → role: member
    - Valid invite code → role determined by INVITE_CODES dict
    - Invalid invite code → 400 error (so people can't guess)
    """
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exists")

    # Resolve role from invite code
    if data.invite_code:
        role = INVITE_CODES.get(data.invite_code.strip())
        if role is None:
            raise HTTPException(status_code=400, detail="Invalid invite code")
    else:
        role = "member"

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_access_token(subject=str(user.id), expires_minutes=60 * 24 * 7)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_access_token(subject=str(user.id), expires_minutes=60 * 24 * 7)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access token.
    The old refresh token is revoked — one-time use.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            data.refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        sub = payload.get("sub")
        jti = payload.get("jti")
        if not sub or not jti:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    revoked = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
    if revoked:
        raise credentials_exception

    try:
        user_id = int(sub)
    except ValueError:
        raise credentials_exception

    user = db.get(User, user_id)
    if not user:
        raise credentials_exception

    db.add(RevokedToken(jti=jti))
    db.commit()

    new_access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_access_token(subject=str(user.id), expires_minutes=60 * 24 * 7)
    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    data: RefreshRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
):
    """
    Revoke both the access token and the refresh token.
    Client must send: { "refresh_token": "..." } in the body.
    """
    # Revoke access token
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        jti = payload.get("jti")
        if jti:
            exists = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
            if not exists:
                db.add(RevokedToken(jti=jti))
    except JWTError:
        pass

    # Revoke refresh token
    try:
        payload = jwt.decode(
            data.refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        jti = payload.get("jti")
        if jti:
            exists = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
            if not exists:
                db.add(RevokedToken(jti=jti))
    except JWTError:
        pass

    db.commit()
    return None


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }