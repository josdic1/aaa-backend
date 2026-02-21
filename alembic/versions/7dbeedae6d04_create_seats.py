"""create seats

Revision ID: 7dbeedae6d04
Revises: 5954ab406847
Create Date: 2026-02-20 19:58:34.196974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7dbeedae6d04'
down_revision: Union[str, Sequence[str], None] = '5954ab406847'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'seats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('table_id', sa.Integer(), nullable=False),
        sa.Column('seat_number', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_seats_id'), 'seats', ['id'], unique=False)
    op.create_index(op.f('ix_seats_table_id'), 'seats', ['table_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_seats_table_id'), table_name='seats')
    op.drop_index(op.f('ix_seats_id'), table_name='seats')
    op.drop_table('seats')