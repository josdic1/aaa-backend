# alembic/versions/adfb3520ae24_seed_menu_items.py
"""seed menu_items

Revision ID: adfb3520ae24
Revises: 4141b0baf29c
Create Date: 2026-02-20 16:05:04.006732

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = "adfb3520ae24"
down_revision: Union[str, Sequence[str], None] = "4141b0baf29c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SEED_ITEMS = [
    {
        "name": "House Salad",
        "description": "Mixed greens, seasonal vegetables, house vinaigrette.",
        "price_cents": 900,
        "dietary_restrictions": ["vegetarian", "gluten_free_option"],
        "is_active": True,
    },
    {
        "name": "Tomato Soup",
        "description": "Roasted tomato soup, basil, olive oil.",
        "price_cents": 800,
        "dietary_restrictions": ["vegetarian", "gluten_free"],
        "is_active": True,
    },
    {
        "name": "Grilled Chicken Plate",
        "description": "Herb grilled chicken, rice, seasonal vegetables.",
        "price_cents": 1800,
        "dietary_restrictions": ["gluten_free"],
        "is_active": True,
    },
    {
        "name": "Vegan Bowl",
        "description": "Quinoa, roasted vegetables, chickpeas, tahini sauce.",
        "price_cents": 1700,
        "dietary_restrictions": ["vegan", "gluten_free"],
        "is_active": True,
    },
    {
        "name": "Cheeseburger",
        "description": "Beef patty, cheddar, lettuce, tomato, house sauce.",
        "price_cents": 1600,
        "dietary_restrictions": ["contains_dairy", "gluten"],
        "is_active": True,
    },
    {
        "name": "Kids Pasta",
        "description": "Butter noodles with parmesan (can omit parmesan).",
        "price_cents": 1100,
        "dietary_restrictions": ["vegetarian", "contains_dairy", "gluten"],
        "is_active": True,
    },
]


def upgrade() -> None:
    conn = op.get_bind()

    # Bind JSONB so we can pass a Python list and let psycopg serialize it correctly.
    dietary_param = sa.bindparam("dietary_restrictions", type_=JSONB)

    # 1) Update existing rows by name (idempotent)
    update_stmt = sa.text(
        """
        UPDATE menu_items
        SET
            description = :description,
            price_cents = :price_cents,
            dietary_restrictions = :dietary_restrictions,
            is_active = :is_active
        WHERE name = CAST(:name AS VARCHAR(140))
        """
    ).bindparams(dietary_param)

    # 2) Insert if missing (idempotent) — explicit casts avoid Postgres type ambiguity
    insert_stmt = sa.text(
        """
        INSERT INTO menu_items (name, description, price_cents, dietary_restrictions, is_active)
        SELECT
            CAST(:name AS VARCHAR(140)),
            CAST(:description AS VARCHAR(500)),
            :price_cents,
            :dietary_restrictions,
            :is_active
        WHERE NOT EXISTS (
            SELECT 1 FROM menu_items WHERE name = CAST(:name AS VARCHAR(140))
        )
        """
    ).bindparams(dietary_param)

    for item in SEED_ITEMS:
        params = {
            "name": item["name"],
            "description": item["description"],
            "price_cents": item["price_cents"],
            "dietary_restrictions": item["dietary_restrictions"],
            "is_active": item["is_active"],
        }
        conn.execute(update_stmt, params)
        conn.execute(insert_stmt, params)


def downgrade() -> None:
    conn = op.get_bind()
    names = [i["name"] for i in SEED_ITEMS]
    conn.execute(sa.text("DELETE FROM menu_items WHERE name = ANY(:names)"), {"names": names})