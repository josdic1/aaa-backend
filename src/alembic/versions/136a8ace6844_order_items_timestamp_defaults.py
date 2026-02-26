"""order_items timestamp defaults

Revision ID: 136a8ace6844
Revises: 8839c3bb117f
Create Date: 2026-02-26

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "136a8ace6844"
down_revision = "8839c3bb117f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) Backfill any existing rows that may have NULLs (defensive)
    op.execute(
        """
        UPDATE order_items
        SET created_at = COALESCE(created_at, TIMEZONE('utc', now())),
            updated_at = COALESCE(updated_at, TIMEZONE('utc', now()))
        WHERE created_at IS NULL OR updated_at IS NULL
        """
    )

    # 2) Add server defaults so future inserts never violate NOT NULL
    op.alter_column(
        "order_items",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("TIMEZONE('utc', now())"),
    )

    op.alter_column(
        "order_items",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("TIMEZONE('utc', now())"),
    )


def downgrade() -> None:
    # Remove server defaults (keep NOT NULL as-is to match schema expectations)
    op.alter_column(
        "order_items",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=None,
    )

    op.alter_column(
        "order_items",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=None,
    )