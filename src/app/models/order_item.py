from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, Dict, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, JSON, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.menu_item import MenuItem


class OrderItem(Base):
    """
    One line item in an attendee's Order.
    Snapshots are mandatory to preserve price/name at order time (audit/fiscal integrity).
    """
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    # "selected" → "ordered" → "served" → "canceled" (or similar flow)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="selected",
        default="selected",
        index=True,
    )

    # REQUIRED snapshots – protect against menu changes after order
    name_snapshot: Mapped[str] = mapped_column(
        String(140),
        nullable=False,
    )

    price_cents_snapshot: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Optional: special requests, customizations, allergies notes, etc.
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        default=None,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("TIMEZONE('utc', now())"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="items",
    )

    menu_item: Mapped["MenuItem"] = relationship(
        "MenuItem",
        back_populates="order_items",
    )