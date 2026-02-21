# app/models/member.py
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User

DIETARY_RESTRICTIONS = [
    "dairy_free",
    "egg_free",
    "fish_allergy",
    "gluten_free",
    "halal",
    "kosher",
    "nut_allergy",
    "peanut_allergy",
    "sesame_allergy",
    "shellfish_allergy",
    "soy_free",
    "vegan",
    "vegetarian",
]

# Defining the enum globally ensures it can be reused 
# and explicitly tells SQLAlchemy not to recreate it in the DB.
dietary_enum = ENUM(
    *DIETARY_RESTRICTIONS,
    name="dietary_restriction_enum",
    create_type=False,
)

class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    relation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Note: Use the dietary_enum variable defined above
    dietary_restrictions: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(dietary_enum),
        nullable=True,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="members",
    )