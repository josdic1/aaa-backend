from typing import Literal
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.user import User



def require_user(user: User = Depends(get_current_user)) -> User:
    """Ensure a logged-in user exists."""
    return user


def require_user_id_match(
    user_id: int,
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the URL user_id matches the authenticated user."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    return current_user


def require_permission(
    entity: str,
    action: Literal["read", "write", "delete"],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> str:
    """
    Enforce role-based permissions for users.
    Rules for 'users' entity:
        - member: can read/write own email/password only
        - staff: cannot access users
        - admin: full CRUD
    Returns: "all" | "own"
    Raises 403 if forbidden
    """

    if entity not in ("users",):
        raise NotImplementedError(f"Permission rules not defined for entity: {entity}")

    # Admin has full access
    if user.role == "admin":
        return "all"

    # Staff cannot access users
    if user.role == "staff":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff cannot access users",
        )

    # Member: can only read/write own record
    if user.role == "member":
        if action in ["read", "write"]:
            return "own"
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Members cannot delete users",
            )

    # Unknown role fallback
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
    )