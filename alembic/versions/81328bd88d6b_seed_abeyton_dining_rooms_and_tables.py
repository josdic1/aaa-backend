"""seed abeyton dining rooms and tables

Revision ID: 81328bd88d6b
Revises: 5f2b79ac396c
Create Date: 2026-02-21 08:39:08.260743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '81328bd88d6b'
down_revision: Union[str, Sequence[str], None] = '5f2b79ac396c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DINING_ROOMS = [
    {"name": "Breakfast Nook",  "description": "Private breakfast room with one table."},
    {"name": "Card Room",       "description": "Private card and dining room."},
    {"name": "Croquet Court",   "description": "Outdoor croquet court with dining."},
    {"name": "Living Room",     "description": "Main living room with dining tables."},
    {"name": "Pool",            "description": "Pool area with cabanas and outdoor tables."},
]

TABLES = [
    # Breakfast Nook
    {"dining_room": "Breakfast Nook", "name": "Table 1", "seat_count": 6},

    # Card Room
    {"dining_room": "Card Room", "name": "Table 1", "seat_count": 10},

    # Croquet Court
    {"dining_room": "Croquet Court", "name": "Table 1", "seat_count": 6},
    {"dining_room": "Croquet Court", "name": "Table 2", "seat_count": 6},
    {"dining_room": "Croquet Court", "name": "Table 3", "seat_count": 6},

    # Living Room
    {"dining_room": "Living Room", "name": "Table 1", "seat_count": 6},
    {"dining_room": "Living Room", "name": "Table 2", "seat_count": 6},
    {"dining_room": "Living Room", "name": "Table 3", "seat_count": 6},

    # Pool
    {"dining_room": "Pool", "name": "Table 1",  "seat_count": 5},
    {"dining_room": "Pool", "name": "Table 2",  "seat_count": 5},
    {"dining_room": "Pool", "name": "Table 3",  "seat_count": 5},
    {"dining_room": "Pool", "name": "Table 4",  "seat_count": 5},
    {"dining_room": "Pool", "name": "Table 5",  "seat_count": 5},
    {"dining_room": "Pool", "name": "Table 6",  "seat_count": 5},
    {"dining_room": "Pool", "name": "Table 7",  "seat_count": 5},
    {"dining_room": "Pool", "name": "Table 8",  "seat_count": 5},
    {"dining_room": "Pool", "name": "Table 9",  "seat_count": 5},
    {"dining_room": "Pool", "name": "Table 10", "seat_count": 5},
    {"dining_room": "Pool", "name": "Table 11", "seat_count": 5},
    {"dining_room": "Pool", "name": "Table 12", "seat_count": 5},
    {"dining_room": "Pool", "name": "Table 13", "seat_count": 6},
]


def upgrade() -> None:
    conn = op.get_bind()

    # Insert dining rooms, get back IDs
    room_ids = {}
    for room in DINING_ROOMS:
        exists = conn.execute(
            sa.text("SELECT id FROM dining_rooms WHERE name = :name"),
            {"name": room["name"]}
        ).scalar()

        if not exists:
            result = conn.execute(
                sa.text(
                    "INSERT INTO dining_rooms (name, description, is_active, created_at) "
                    "VALUES (:name, :description, true, now()) RETURNING id"
                ),
                {"name": room["name"], "description": room["description"]}
            )
            room_ids[room["name"]] = result.scalar()
        else:
            room_ids[room["name"]] = exists

    # Insert tables
    for table in TABLES:
        room_id = room_ids[table["dining_room"]]
        exists = conn.execute(
            sa.text(
                "SELECT 1 FROM tables WHERE dining_room_id = :room_id AND name = :name"
            ),
            {"room_id": room_id, "name": table["name"]}
        ).scalar()

        if not exists:
            conn.execute(
                sa.text(
                    "INSERT INTO tables (dining_room_id, name, seat_count, is_active, created_at) "
                    "VALUES (:room_id, :name, :seat_count, true, now())"
                ),
                {"room_id": room_id, "name": table["name"], "seat_count": table["seat_count"]}
            )


def downgrade() -> None:
    conn = op.get_bind()
    for table in TABLES:
        conn.execute(
            sa.text("DELETE FROM tables WHERE name = :name"),
            {"name": table["name"]}
        )
    for room in DINING_ROOMS:
        conn.execute(
            sa.text("DELETE FROM dining_rooms WHERE name = :name"),
            {"name": room["name"]}
        )