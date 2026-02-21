from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from jose import JWTError, jwt

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


# --- Schemas ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


# --- Endpoints ---
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Public user registration (role=member)."""
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role="member",  # enforce member role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
):
    # decode token to extract jti
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        jti = payload.get("jti")
        if not jti or not isinstance(jti, str):
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # insert revoked token (idempotent-ish: ignore duplicates)
    exists = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
    if not exists:
        db.add(RevokedToken(jti=jti))
        db.commit()

    return None


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }