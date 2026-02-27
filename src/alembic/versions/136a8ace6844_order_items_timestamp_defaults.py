"""order_items timestamp defaults

Revision ID: 136a8ace6844
Revises: 8839c3bb117f
Create Date: 2026-02-26

Schema-only: ensure server-side UTC defaults for order_items timestamps.
Do NOT backfill rows here; fresh DB has none and backfill can fail if table order differs.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "136a8ace6844"
down_revision = "8839c3bb117f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
DO $$
BEGIN
  IF to_regclass('public.order_items') IS NOT NULL THEN
    ALTER TABLE order_items
      ALTER COLUMN created_at SET DEFAULT TIMEZONE('utc', now());
    ALTER TABLE order_items
      ALTER COLUMN updated_at SET DEFAULT TIMEZONE('utc', now());
  END IF;
END$$;
""")


def downgrade() -> None:
    op.execute("""
DO $$
BEGIN
  IF to_regclass('public.order_items') IS NOT NULL THEN
    ALTER TABLE order_items ALTER COLUMN created_at DROP DEFAULT;
    ALTER TABLE order_items ALTER COLUMN updated_at DROP DEFAULT;
  END IF;
END$$;
""")
