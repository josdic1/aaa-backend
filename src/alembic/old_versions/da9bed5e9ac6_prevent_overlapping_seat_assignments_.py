"""prevent overlapping seat assignments per table

Revision ID: da9bed5e9ac6
Revises: 7d69ab2748d9
Create Date: 2026-02-24 20:33:58.343971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "da9bed5e9ac6"
down_revision: Union[str, Sequence[str], None] = "7d69ab2748d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EXCLUSION_NAME = "excl_seat_assignments_table_overlap"
CHECK_NAME = "ck_seat_assignments_end_after_start"


def upgrade() -> None:
    """Upgrade schema."""
    # Needed so GiST can index/compare btree types like INTEGER in an EXCLUDE constraint
    op.execute('CREATE EXTENSION IF NOT EXISTS btree_gist')

    # Sanity: prevent zero/negative durations
    op.create_check_constraint(
        CHECK_NAME,
        "seat_assignments",
        "end_at > start_at",
    )

    # Core rule:
    # For the same table_id, time ranges may not overlap.
    # '[)' makes end exclusive so 6:00–7:00 does NOT overlap 7:00–8:00.
    op.execute(
        f"""
        ALTER TABLE seat_assignments
        ADD CONSTRAINT {EXCLUSION_NAME}
        EXCLUDE USING gist (
          table_id WITH =,
          tstzrange(start_at, end_at, '[)') WITH &&
        );
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(f"ALTER TABLE seat_assignments DROP CONSTRAINT IF EXISTS {EXCLUSION_NAME}")
    op.drop_constraint(CHECK_NAME, "seat_assignments", type_="check")
    # Intentionally do NOT drop the extension; it may be used elsewhere.