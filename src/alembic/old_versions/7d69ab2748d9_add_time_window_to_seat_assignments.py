"""add time window to seat assignments

Revision ID: 7d69ab2748d9
Revises: fd8737e7375d
Create Date: 2026-02-24 20:27:31.197908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7d69ab2748d9"
down_revision: Union[str, Sequence[str], None] = "fd8737e7375d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Keep your existing reservation_code adjustments
    op.alter_column(
        "reservations",
        "reservation_code",
        existing_type=sa.VARCHAR(length=64),
        type_=sa.String(length=80),
        nullable=True,
    )
    op.drop_index(op.f("ix_reservations_reservation_code"), table_name="reservations")
    op.create_index(
        op.f("ix_reservations_reservation_code"),
        "reservations",
        ["reservation_code"],
        unique=True,
    )

    # 1) Add columns nullable first so existing rows don't fail
    op.add_column(
        "seat_assignments",
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "seat_assignments",
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 2) Backfill from reservations (date + start_time/end_time)
    # If end_time is NULL, default to +90 minutes
    op.execute(
        """
        UPDATE seat_assignments sa
        SET
          start_at = (r.date + r.start_time)::timestamptz,
          end_at   = COALESCE(
                      (r.date + r.end_time)::timestamptz,
                      ((r.date + r.start_time) + interval '90 minutes')::timestamptz
                    )
        FROM reservations r
        WHERE r.id = sa.reservation_id
        """
    )

    # 3) Enforce NOT NULL after backfill
    op.alter_column("seat_assignments", "start_at", nullable=False)
    op.alter_column("seat_assignments", "end_at", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the new columns first
    op.drop_column("seat_assignments", "end_at")
    op.drop_column("seat_assignments", "start_at")

    # Revert reservation_code index/type changes (as your original)
    op.drop_index(op.f("ix_reservations_reservation_code"), table_name="reservations")
    op.create_index(
        op.f("ix_reservations_reservation_code"),
        "reservations",
        ["reservation_code"],
        unique=False,
    )
    op.alter_column(
        "reservations",
        "reservation_code",
        existing_type=sa.String(length=80),
        type_=sa.VARCHAR(length=64),
        nullable=False,
    )