# alembic/versions/fe43eeb6784d_attendees_require_member_or_guest_name.py
"""attendees require member or guest_name

Revision ID: fe43eeb6784d
Revises: 0490c6a4610a
"""

from alembic import op
import sqlalchemy as sa

revision = "fe43eeb6784d"
down_revision = "0490c6a4610a"
branch_labels = None
depends_on = None

def upgrade():
    op.create_check_constraint(
        "ck_reservation_attendees_member_or_guest",
        "reservation_attendees",
        sa.text("(member_id IS NOT NULL) OR (guest_name IS NOT NULL AND length(btrim(guest_name)) > 0)")
    )

def downgrade():
    op.drop_constraint(
        "ck_reservation_attendees_member_or_guest",
        "reservation_attendees",
        type_="check"
    )