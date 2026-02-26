"""create messages table

Revision ID: 02b291c4315a
Revises: 3de4a3bd5ffd
Create Date: 2026-02-20 17:36:14.975082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "02b291c4315a"
down_revision: Union[str, Sequence[str], None] = "3de4a3bd5ffd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Explicit constraint name to avoid None (and to make downgrades reliable)
FK_MESSAGES_SENDER_USER_ID = "fk_messages_sender_user_id_users"


def upgrade() -> None:
    """Upgrade schema."""
    # Add new column first
    op.add_column("messages", sa.Column("sender_user_id", sa.Integer(), nullable=False))

    # Drop old indexes
    op.drop_index(op.f("ix_messages_attendee_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_user_id"), table_name="messages")

    # Create new index
    op.create_index(
        op.f("ix_messages_sender_user_id"),
        "messages",
        ["sender_user_id"],
        unique=False,
    )

    # Drop old foreign keys
    op.drop_constraint(op.f("messages_attendee_id_fkey"), "messages", type_="foreignkey")
    op.drop_constraint(op.f("messages_user_id_fkey"), "messages", type_="foreignkey")

    # Create new foreign key with explicit name
    op.create_foreign_key(
        FK_MESSAGES_SENDER_USER_ID,
        "messages",
        "users",
        ["sender_user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Drop old columns last
    op.drop_column("messages", "attendee_id")
    op.drop_column("messages", "user_id")


def downgrade() -> None:
    """Downgrade schema."""
    # Re-add old columns
    op.add_column(
        "messages",
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "messages",
        sa.Column("attendee_id", sa.INTEGER(), autoincrement=False, nullable=True),
    )

    # Drop the new FK (explicit name)
    op.drop_constraint(FK_MESSAGES_SENDER_USER_ID, "messages", type_="foreignkey")

    # Recreate old foreign keys
    op.create_foreign_key(
        op.f("messages_user_id_fkey"),
        "messages",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("messages_attendee_id_fkey"),
        "messages",
        "reservation_attendees",
        ["attendee_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Swap indexes back
    op.drop_index(op.f("ix_messages_sender_user_id"), table_name="messages")
    op.create_index(op.f("ix_messages_user_id"), "messages", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_messages_attendee_id"),
        "messages",
        ["attendee_id"],
        unique=False,
    )

    # Drop new column
    op.drop_column("messages", "sender_user_id")