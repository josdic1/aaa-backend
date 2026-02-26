"""add reservation_code to reservations

Revision ID: fd8737e7375d
Revises: 09046051e190
Create Date: 2026-02-24 15:57:11.530197

"""
from __future__ import annotations
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd8737e7375d'
down_revision: Union[str, Sequence[str], None] = '09046051e190'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Add column as nullable first (safe for existing rows)
    op.add_column(
        "reservations",
        sa.Column("reservation_code", sa.String(length=64), nullable=True),
    )

    # 2) Backfill existing rows with a deterministic code
    # Format: R{ID}-{YYYYMMDD}-{HHMM}
    op.execute(
        """
        UPDATE reservations
        SET reservation_code =
          'R' || id::text || '-' ||
          to_char(date, 'YYYYMMDD') || '-' ||
          replace(to_char(start_time, 'HH24:MI'), ':', '')
        WHERE reservation_code IS NULL
        """
    )

    # 3) Enforce NOT NULL after backfill
    op.alter_column("reservations", "reservation_code", nullable=False)

    # Optional (recommended): index for quick lookup
    op.create_index(
        "ix_reservations_reservation_code",
        "reservations",
        ["reservation_code"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_reservations_reservation_code", table_name="reservations")
    op.drop_column("reservations", "reservation_code")