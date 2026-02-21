# alembic/versions/0490c6a4610a_create_reservations_reservation_attendees.py
"""create reservations + reservation_attendees

Revision ID: 0490c6a4610a
Revises: c677edcaa079
Create Date: 2026-02-20 14:31:54.518034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0490c6a4610a"
down_revision: Union[str, Sequence[str], None] = "c677edcaa079"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Reuse existing DB enum type; do NOT recreate
dietary_enum = postgresql.ENUM(
    "dairy_free",
    "egg_free",
    "fish_allergy",
    "gluten_free",
    "halal",
    "kosher",
    "nut_allergy",
    "peanut_allergy",
    "sesame_allergy",
    "shellfish_allergy",
    "soy_free",
    "vegan",
    "vegetarian",
    name="dietary_restriction_enum",
    create_type=False,
)


def upgrade() -> None:
    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="draft", nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reservations_date"), "reservations", ["date"], unique=False)
    op.create_index(op.f("ix_reservations_status"), "reservations", ["status"], unique=False)
    op.create_index(op.f("ix_reservations_user_id"), "reservations", ["user_id"], unique=False)

    op.create_table(
        "reservation_attendees",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reservation_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=True),
        sa.Column("guest_name", sa.String(length=120), nullable=True),
        sa.Column("dietary_restrictions", postgresql.ARRAY(dietary_enum), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("selection_confirmed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reservation_id"], ["reservations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reservation_attendees_member_id"),
        "reservation_attendees",
        ["member_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reservation_attendees_reservation_id"),
        "reservation_attendees",
        ["reservation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_reservation_attendees_reservation_id"), table_name="reservation_attendees")
    op.drop_index(op.f("ix_reservation_attendees_member_id"), table_name="reservation_attendees")
    op.drop_table("reservation_attendees")

    op.drop_index(op.f("ix_reservations_user_id"), table_name="reservations")
    op.drop_index(op.f("ix_reservations_status"), table_name="reservations")
    op.drop_index(op.f("ix_reservations_date"), table_name="reservations")
    op.drop_table("reservations")