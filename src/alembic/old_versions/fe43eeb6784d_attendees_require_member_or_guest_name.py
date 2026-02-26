"""add_member_server_defaults

Revision ID: c5d03ac4c71e
Revises: da9bed5e9ac6
Create Date: 2026-02-26 12:04:52.198929
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c5d03ac4c71e'
down_revision: Union[str, Sequence[str], None] = 'da9bed5e9ac6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Unique constraint naming fix (safe drop if exists)
    try:
        op.drop_constraint('dining_rooms_name_key', 'dining_rooms', type_='unique')
    except Exception:
        pass  # already dropped or different name

    op.create_unique_constraint(
        op.f('uq_dining_rooms_name'), 'dining_rooms', ['name']
    )

    # 2. Apply server-side UTC defaults + enforce NOT NULL (fixes IntegrityError)
    op.alter_column(
        'members',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("TIMEZONE('utc', now())")
    )
    op.alter_column(
        'members',
        'updated_at',
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("TIMEZONE('utc', now())")
    )

    # 3. Other columns (non-nullable enforcement)
    op.alter_column(
        'members',
        'dietary_restrictions',
        existing_type=postgresql.ARRAY(postgresql.ENUM(
            'dairy_free', 'egg_free', 'fish_allergy', 'gluten_free',
            'halal', 'kosher', 'nut_allergy', 'peanut_allergy',
            'sesame_allergy', 'shellfish_allergy', 'soy_free',
            'vegan', 'vegetarian', name='dietary_restriction_enum'
        )),
        nullable=False
    )

    op.alter_column(
        'order_items',
        'name_snapshot',
        existing_type=sa.VARCHAR(length=140),
        nullable=False
    )

    op.alter_column(
        'order_items',
        'price_cents_snapshot',
        existing_type=sa.INTEGER(),
        nullable=False
    )

    op.alter_column(
        'reservation_attendees',
        'dietary_restrictions',
        existing_type=postgresql.ARRAY(postgresql.ENUM(
            'dairy_free', 'egg_free', 'fish_allergy', 'gluten_free',
            'halal', 'kosher', 'nut_allergy', 'peanut_allergy',
            'sesame_allergy', 'shellfish_allergy', 'soy_free',
            'vegan', 'vegetarian', name='dietary_restriction_enum'
        )),
        nullable=False,
        existing_server_default=sa.text("'{}'::dietary_restriction_enum[]")
    )

    # 4. Foreign key
    op.create_foreign_key(
        op.f('fk_reservation_attendees_member_id_members'),
        'reservation_attendees',
        'members',
        ['member_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f('fk_reservation_attendees_member_id_members'),
        'reservation_attendees',
        type_='foreignkey'
    )

    # Remove server defaults (safe even if not present)
    op.execute("ALTER TABLE members ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE members ALTER COLUMN updated_at DROP DEFAULT")

    # Revert non-nullable columns
    op.alter_column(
        'reservation_attendees',
        'dietary_restrictions',
        existing_type=postgresql.ARRAY(postgresql.ENUM(...)),
        nullable=True,
        existing_server_default=sa.text("'{}'::dietary_restriction_enum[]")
    )

    op.alter_column(
        'order_items',
        'price_cents_snapshot',
        existing_type=sa.INTEGER(),
        nullable=True
    )

    op.alter_column(
        'order_items',
        'name_snapshot',
        existing_type=sa.VARCHAR(length=140),
        nullable=True
    )

    op.alter_column(
        'members',
        'dietary_restrictions',
        existing_type=postgresql.ARRAY(postgresql.ENUM(...)),
        nullable=True
    )

    op.drop_constraint(
        op.f('uq_dining_rooms_name'),
        'dining_rooms',
        type_='unique'
    )
    op.create_unique_constraint(
        'dining_rooms_name_key',
        'dining_rooms',
        ['name']
    )