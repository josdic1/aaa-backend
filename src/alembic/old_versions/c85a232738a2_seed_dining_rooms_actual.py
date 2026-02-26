"""seed dining rooms actual

Revision ID: c85a232738a2
Revises: c010172491bd
Create Date: 2026-02-20 18:16:48.553480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c85a232738a2'
down_revision: Union[str, Sequence[str], None] = 'c010172491bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO dining_rooms (name, description, is_active, created_at)
        VALUES
        ('Main Dining Room', 'Primary floor seating', True, now()),
        ('Bar', 'Bar seating area', True, now()),
        ('Patio', 'Outdoor seating', True, now()),
        ('Private Room', 'Private events and parties', True, now());
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
