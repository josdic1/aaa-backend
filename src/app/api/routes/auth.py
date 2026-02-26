from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import Optional

from app.api.deps.auth import (
    verify_password,
    hash_password,
    create_access_token,
    get_current_user,
)
from app.api.deps.db import get_db
from app.core.config import get_settings
from app.models.revoked_token import RevokedToken
from app.models.user import User

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Auth"])

# --- Schemas ---

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class RefreshRequest(BaseModel):
    refresh_token: str

# --- Routes ---

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: UserRegister, 
    db: Session = Depends(get_db)
):
    """
    Register a new User and automatically create their Primary Member profile.
    This ensures the user is immediately 'seatable' in the reservation system.
    """
    from app.models.member import Member  # Local import to prevent circular dependency

    email_clean = request.email.lower().strip()
    
    # Check if user already exists
    if db.query(User).filter(User.email == email_clean).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Email already registered"
        )

    # 1. Create the User record
    user = User(
        email=email_clean,
        password_hash=hash_password(request.password),
        role="member",
        is_active=True,
    )
    db.add(user)
    db.flush()  # Push to DB to generate user.id

    # 2. Create the Primary Member profile
    # Use full_name if provided, otherwise derive from email
    name = request.full_name or email_clean.split("@")[0].capitalize()
    member = Member(
        user_id=user.id,
        name=name,
        relation="Primary"
    )
    db.add(member)
    
    db.commit()
    db.refresh(user)

    # 3. Generate tokens for immediate login
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_access_token(subject=str(user.id), is_refresh=True)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Standard OAuth2 login flow."""
    user = db.query(User).filter(User.email == form_data.username.lower().strip()).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is deactivated")

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_access_token(subject=str(user.id), is_refresh=True)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    data: RefreshRequest, 
    db: Session = Depends(get_db)
):
    """Exchange a refresh token for a new set of tokens (Token Rotation)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or revoked refresh token",
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
        token_type = payload.get("type")

        if not isinstance(sub, str) or not isinstance(jti, str) or token_type != "refresh":
            raise credentials_exception

        user_id = int(sub)
    except (JWTError, ValueError):
        raise credentials_exception

    # Check if token has been revoked
    revoked = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
    if revoked:
        raise credentials_exception

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise credentials_exception

    # Revoke old token and rotate
    db.add(RevokedToken(jti=jti))
    db.commit()

    return TokenResponse(
        access_token=create_access_token(subject=str(user.id)),
        refresh_token=create_access_token(subject=str(user.id), is_refresh=True)
    )


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user's profile info."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }