"""orders_timestamp_defaults

Revision ID: 9860397f4821
Revises: 8839c3bb117f
Create Date: 2026-02-26

Schema-only: ensure server-side UTC defaults for orders timestamps.
Do NOT backfill rows here; fresh DB has none and backfill can fail if table order differs.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "9860397f4821"
down_revision = "fe535f23d0c8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make this migration safe on a brand new database.
    # If the table doesn't exist yet (due to revision ordering), do nothing.
    op.execute("""
DO $$
BEGIN
  IF to_regclass('public.orders') IS NOT NULL THEN
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
