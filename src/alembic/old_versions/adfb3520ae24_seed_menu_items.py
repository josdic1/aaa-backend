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
    "name": "Hudson Valley Cheese Board",
    "description": "Cypress Hill Farms blue cheese, Murray’s Farms young gouda, Grafton Farms aged cheddar, hard salami, dried fruit, olives, crostini.",
    "price_cents": 2400,
    "dietary_restrictions": [],
    "is_active": True
  },
  {
    "name": "Burrata",
    "description": "Tomato confit, olive oil, roasted garlic, cracked fresh pepper. Served with crostini or gluten-free crackers.",
    "price_cents": 2000,
    "dietary_restrictions": ["vegetarian"],
    "is_active": True
  },
  {
    "name": "Jumbo Bavarian Pretzel",
    "description": "Butter brushed, sea salt, honey dijon.",
    "price_cents": 1400,
    "dietary_restrictions": ["vegetarian"],
    "is_active": True
  },
  {
    "name": "Mezze Platter",
    "description": "Grilled soft flatbread, sun-dried tomato hummus, stuffed grape leaves, marinated olives, feta cheese.",
    "price_cents": 1900,
    "dietary_restrictions": ["vegetarian"],
    "is_active": True
  },
  {
    "name": "Create Your Own Salad or Bowl",
    "description": "Choose greens, grains, proteins, vegetables, fruits, cheeses, and dressing. Greens sourced from Satur Farm, Norwich Meadows Farm, and Hepworth Farm.",
    "price_cents": 1600,
    "dietary_restrictions": [],
    "is_active": True
  },
  {
    "name": "Add Grilled Chicken",
    "description": "Protein add-on for salads/bowls.",
    "price_cents": 700,
    "dietary_restrictions": ["gluten_free", "dairy_free"],
    "is_active": True
  },
  {
    "name": "Add Grilled Salmon",
    "description": "Protein add-on for salads/bowls.",
    "price_cents": 900,
    "dietary_restrictions": ["gluten_free", "dairy_free"],
    "is_active": True
  },
  {
    "name": "Add Grilled Tuna",
    "description": "Protein add-on for salads/bowls.",
    "price_cents": 1000,
    "dietary_restrictions": ["gluten_free", "dairy_free"],
    "is_active": True
  },
  {
    "name": "Add Fried Falafel",
    "description": "Protein add-on for salads/bowls.",
    "price_cents": 700,
    "dietary_restrictions": ["vegetarian"],
    "is_active": True
  },
  {
    "name": "Add Hard Boiled Egg",
    "description": "Protein add-on for salads/bowls.",
    "price_cents": 300,
    "dietary_restrictions": ["gluten_free", "vegetarian"],
    "is_active": True
  },
  {
    "name": "Add Bacon",
    "description": "Protein add-on for salads/bowls.",
    "price_cents": 400,
    "dietary_restrictions": ["gluten_free", "dairy_free"],
    "is_active": True
  },
  {
    "name": "Classic Chicken Salad",
    "description": "Herb mayonnaise. Served on Martin’s bun or whole wheat wrap.",
    "price_cents": 1800,
    "dietary_restrictions": ["gluten_free"],
    "is_active": True
  },
  {
    "name": "Free Range Turkey Club",
    "description": "Bacon, lettuce, tomato chutney, sliced tomato, stone ground wheat bread.",
    "price_cents": 2100,
    "dietary_restrictions": [],
    "is_active": True
  },
  {
    "name": "Fried Chicken Sandwich",
    "description": "Fried chicken thigh on Martin’s roll with hot honey, house-made pickles, and coleslaw.",
    "price_cents": 2000,
    "dietary_restrictions": [],
    "is_active": True
  },
  {
    "name": "Angus Beef Hamburger",
    "description": "Fresh off the grill. Gluten-free bread available upon request.",
    "price_cents": 1900,
    "dietary_restrictions": [],
    "is_active": True
  },
  {
    "name": "Turkey Burger",
    "description": "Fresh off the grill. Gluten-free bread available upon request.",
    "price_cents": 1900,
    "dietary_restrictions": [],
    "is_active": True
  },
  {
    "name": "Grilled Salmon (Sandwich Style)",
    "description": "Fresh off the grill. Gluten-free bread available upon request.",
    "price_cents": 2200,
    "dietary_restrictions": ["dairy_free"],
    "is_active": True
  },
  {
    "name": "Grilled Chicken Breast (Sandwich Style)",
    "description": "Fresh off the grill. Gluten-free bread available upon request.",
    "price_cents": 1900,
    "dietary_restrictions": ["dairy_free"],
    "is_active": True
  },
  {
    "name": "Beyond Burger",
    "description": "Plant-based burger. Gluten-free bread available upon request.",
    "price_cents": 2000,
    "dietary_restrictions": ["vegan", "vegetarian", "dairy_free"],
    "is_active": True
  },
  {
    "name": "Quesadilla (Chicken)",
    "description": "Cheddar melted in a flour tortilla. Served with pico de gallo.",
    "price_cents": 1700,
    "dietary_restrictions": [],
    "is_active": True
  },
  {
    "name": "Quesadilla (Cheese)",
    "description": "Cheddar melted in a flour tortilla. Served with pico de gallo.",
    "price_cents": 1500,
    "dietary_restrictions": ["vegetarian"],
    "is_active": True
  },
  {
    "name": "All-Beef Hot Dog",
    "description": "All-beef hot dog on Martin’s bun. Optional cheddar or American cheese.",
    "price_cents": 1400,
    "dietary_restrictions": [],
    "is_active": True
  },
  {
    "name": "Hot Dog — Add Cheese",
    "description": "Add cheddar or American cheese.",
    "price_cents": 200,
    "dietary_restrictions": ["vegetarian"],
    "is_active": True
  },
  {
    "name": "Lobster Roll",
    "description": "Lobster salad on a toasted buttered roll, lemon aioli, and a lemon wedge.",
    "price_cents": 3400,
    "dietary_restrictions": [],
    "is_active": True
  },
  {
    "name": "Pizza Flatbread",
    "description": "San Marzano tomato sauce, fresh mozzarella, basil.",
    "price_cents": 1800,
    "dietary_restrictions": ["vegetarian"],
    "is_active": True
  },
  {
    "name": "Grilled Strip Steak (Dinner Only)",
    "description": "Grilled NY strip steak, wild mushroom haricot verts, and a baked potato with sour cream and chopped chives.",
    "price_cents": 4200,
    "dietary_restrictions": [],
    "is_active": True
  },
  {
    "name": "Classic Potato Salad",
    "description": "Grill side.",
    "price_cents": 900,
    "dietary_restrictions": ["vegetarian", "gluten_free"],
    "is_active": True
  },
  {
    "name": "Baked Potato",
    "description": "With sour cream and butter.",
    "price_cents": 900,
    "dietary_restrictions": ["vegetarian", "gluten_free"],
    "is_active": True
  },
  {
    "name": "Grilled Vegetable Medley",
    "description": "Grill side.",
    "price_cents": 1100,
    "dietary_restrictions": [
      "vegan",
      "vegetarian",
      "gluten_free",
      "dairy_free"
    ],
    "is_active": True
  },
  {
    "name": "Potato Chips",
    "description": "Grill side.",
    "price_cents": 600,
    "dietary_restrictions": [
      "vegan",
      "vegetarian",
      "gluten_free",
      "dairy_free"
    ],
    "is_active": True
  },
  {
    "name": "Grilled Chicken Strips",
    "description": "Kids option.",
    "price_cents": 1100,
    "dietary_restrictions": ["gluten_free", "dairy_free"],
    "is_active": True
  },
  {
    "name": "Mac & Cheese",
    "description": "Kids option (GF).",
    "price_cents": 1200,
    "dietary_restrictions": ["gluten_free", "vegetarian"],
    "is_active": True
  },
  {
    "name": "Classic Pound Cake",
    "description": "With a vanilla glaze.",
    "price_cents": 900,
    "dietary_restrictions": ["vegetarian"],
    "is_active": True
  },
  {
    "name": "Blondies",
    "description": "From the bake shop.",
    "price_cents": 800,
    "dietary_restrictions": ["vegetarian"],
    "is_active": True
  },
  {
    "name": "Churros",
    "description": "Rolled in cinnamon sugar and served with chocolate chili sauce.",
    "price_cents": 1000,
    "dietary_restrictions": ["vegetarian"],
    "is_active": True
  },
  {
    "name": "Fudge Brownies",
    "description": "From the bake shop.",
    "price_cents": 800,
    "dietary_restrictions": ["vegetarian"],
    "is_active": True
  },
  {
    "name": "Oatmeal & Chocolate Chip Cookies",
    "description": "From the bake shop.",
    "price_cents": 600,
    "dietary_restrictions": ["vegetarian"],
    "is_active": True
  },
  {
    "name": "Ice Cream Sundae Bar",
    "description": "Vanilla, chocolate, strawberry, coffee, soy-based, coconut (DF). Includes topping bar.",
    "price_cents": 1200,
    "dietary_restrictions": ["vegetarian"],
    "is_active": True
  },
  {
    "name": "Popsicle — Strawberry",
    "description": "Vegan, dairy free.",
    "price_cents": 500,
    "dietary_restrictions": [
      "vegan",
      "vegetarian",
      "dairy_free",
      "gluten_free"
    ],
    "is_active": True
  },
  {
    "name": "Popsicle — Tangerine",
    "description": "Vegan, dairy free.",
    "price_cents": 500,
    "dietary_restrictions": [
      "vegan",
      "vegetarian",
      "dairy_free",
      "gluten_free"
    ],
    "is_active": True
  },
  {
    "name": "Popsicle — Raspberry",
    "description": "Vegan, dairy free.",
    "price_cents": 500,
    "dietary_restrictions": [
      "vegan",
      "vegetarian",
      "dairy_free",
      "gluten_free"
    ],
    "is_active": True
  }
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