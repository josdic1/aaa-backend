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
    oauth2_scheme,
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
    invite_code: Optional[str] = None      # C-02: added

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):            # C-01: added
    refresh_token: Optional[str] = None

# --- Routes ---

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: UserRegister,
    db: Session = Depends(get_db)
):
    from app.models.member import Member

    email_clean = request.email.lower().strip()

    if db.query(User).filter(User.email == email_clean).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # C-02: role determined server-side from invite code
    role = "member"
    if request.invite_code:
        if settings.STAFF_INVITE_CODE and request.invite_code == settings.STAFF_INVITE_CODE:
            role = "staff"
        else:
            raise HTTPException(status_code=400, detail="Invalid invite code")

    user = User(
        email=email_clean,
        password_hash=hash_password(request.password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.flush()

    name = request.full_name or email_clean.split("@")[0].capitalize()
    member = Member(user_id=user.id, name=name, relation="Primary")
    db.add(member)

    db.commit()
    db.refresh(user)

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_access_token(subject=str(user.id), is_refresh=True)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
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

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    data: RefreshRequest,
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or revoked refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(data.refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        sub = payload.get("sub")
        jti = payload.get("jti")
        token_type = payload.get("type")

        if not isinstance(sub, str) or not isinstance(jti, str) or token_type != "refresh":
            raise credentials_exception

        user_id = int(sub)
    except (JWTError, ValueError):
        raise credentials_exception

    revoked = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
    if revoked:
        raise credentials_exception

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise credentials_exception

    db.add(RevokedToken(jti=jti))
    db.commit()

    return TokenResponse(
        access_token=create_access_token(subject=str(user.id)),
        refresh_token=create_access_token(subject=str(user.id), is_refresh=True)
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)  # C-01
def logout(
    payload: LogoutRequest,
    current_user: User = Depends(get_current_user),
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    jtis_to_revoke = []

    if token:
        try:
            p = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            if jti := p.get("jti"):
                jtis_to_revoke.append(jti)
        except JWTError:
            pass

    if payload.refresh_token:
        try:
            p = jwt.decode(payload.refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            if jti := p.get("jti"):
                jtis_to_revoke.append(jti)
        except JWTError:
            pass

    for jti in jtis_to_revoke:
        if not db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
            db.add(RevokedToken(jti=jti))

    if jtis_to_revoke:
        db.commit()

    return None


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }