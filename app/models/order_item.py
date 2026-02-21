# app/models/order_item.py
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.menu_item import MenuItem


class OrderItem(Base):
    """
    One selection within an attendee's Order.

    History rules:
    - Do not delete rows; use status transitions instead.
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

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")

    # examples: "selected", "ordered", "served", "canceled"
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="selected",
        server_default="selected",
        index=True,
    )

    # snapshot fields for history (optional but useful)
    name_snapshot: Mapped[Optional[str]] = mapped_column(String(140), nullable=True)
    price_cents_snapshot: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="order_items")