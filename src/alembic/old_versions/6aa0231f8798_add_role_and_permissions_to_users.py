# alembic/versions/6aa0231f8798_add_role_and_permissions_to_users.py
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6aa0231f8798'
down_revision: Union[str, Sequence[str], None] = 'd6cd046b0fa4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add role and permissions columns to users"""
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), nullable=False, server_default="member", index=True),
    )
    op.add_column(
        "users",
        sa.Column("permissions", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema: remove role and permissions columns from users"""
    op.drop_column("users", "permissions")
    op.drop_column("users", "role")