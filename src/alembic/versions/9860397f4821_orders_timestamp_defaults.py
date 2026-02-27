"""orders_timestamp_defaults

Revision ID: 9860397f4821
Revises: 8839c3bb117f
Create Date: 2026-02-26

Ensures orders.created_at / orders.updated_at have server-side UTC defaults and
backfills any existing NULLs (defensive).
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "9860397f4821"
down_revision = "8839c3bb117f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
DO $$
BEGIN
  IF to_regclass('public.orders') IS NOT NULL THEN
    -- Backfill NULLs (defensive)
    UPDATE orders
    SET created_at = TIMEZONE('utc', now())
    WHERE created_at IS NULL;

    UPDATE orders
    SET updated_at = TIMEZONE('utc', now())
    WHERE updated_at IS NULL;

    -- Ensure server defaults
    ALTER TABLE orders
      ALTER COLUMN created_at SET DEFAULT TIMEZONE('utc', now());

    ALTER TABLE orders
      ALTER COLUMN updated_at SET DEFAULT TIMEZONE('utc', now());
  END IF;
END$$;
""")


def downgrade() -> None:
    op.execute("""
DO $$
BEGIN
  IF to_regclass('public.orders') IS NOT NULL THEN
    ALTER TABLE orders ALTER COLUMN created_at DROP DEFAULT;
    ALTER TABLE orders ALTER COLUMN updated_at DROP DEFAULT;
  END IF;
END$$;
""")
