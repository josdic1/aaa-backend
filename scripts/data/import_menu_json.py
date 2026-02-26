from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# NOTE:
# This import must match your project.
# You already use this model in your API routes, so it should exist.
from app.models.menu_item import MenuItem


def _get_db_url() -> str:
    """
    Prefer env var DATABASE_URL / SQLALCHEMY_DATABASE_URI.
    Fallback to the same Postgres URL you’ve been using in psql (local dev).
    """
    return (
        os.getenv("DATABASE_URL")
        or os.getenv("SQLALCHEMY_DATABASE_URI")
        or "postgresql://joshdicker@localhost:5432/aaa"
    )


def _load_menu_items(json_path: Path) -> List[Dict[str, Any]]:
    data = json.loads(json_path.read_text(encoding="utf-8"))

    if not isinstance(data, list):
        raise ValueError("menu.json must be a JSON array of items.")

    required = {"name", "description", "price_cents", "dietary_restrictions", "is_active"}
    cleaned: List[Dict[str, Any]] = []

    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Item #{idx} must be an object.")

        missing = required - set(item.keys())
        if missing:
            raise ValueError(f"Item #{idx} missing keys: {sorted(missing)}")

        # Normalize types
        name = str(item["name"]).strip()
        description = str(item["description"]).strip() if item["description"] is not None else ""
        price_cents = int(item["price_cents"] or 0)
        dietary = item["dietary_restrictions"] or []
        if not isinstance(dietary, list):
            raise ValueError(f"Item '{name}': dietary_restrictions must be an array.")
        dietary = [str(x) for x in dietary]
        is_active = bool(item["is_active"])

        cleaned.append(
            {
                "name": name,
                "description": description,
                "price_cents": price_cents,
                "dietary_restrictions": dietary,  # SQLAlchemy JSON/JSONB expects Python list
                "is_active": is_active,
            }
        )

    return cleaned


def _upsert_by_name(
    session,
    items: List[Dict[str, Any]],
) -> Tuple[int, int]:
    """
    Upsert strategy:
    - If MenuItem with same name exists: update fields
    - Else: insert new row
    Returns (inserted_count, updated_count)
    """
    inserted = 0
    updated = 0

    for payload in items:
        existing: Optional[MenuItem] = (
            session.query(MenuItem).filter(MenuItem.name == payload["name"]).one_or_none()
        )

        if existing:
            existing.description = payload["description"]
            existing.price_cents = payload["price_cents"]
            existing.dietary_restrictions = payload["dietary_restrictions"]
            existing.is_active = payload["is_active"]
            updated += 1
        else:
            session.add(MenuItem(**payload))
            inserted += 1

    return inserted, updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Import menu.json into Postgres menu_items.")
    parser.add_argument(
        "--file",
        default="menu.json",
        help="Path to menu.json (default: ./menu.json)",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Delete all rows from menu_items before importing (DANGEROUS).",
    )

    args = parser.parse_args()

    json_path = Path(args.file).resolve()
    if not json_path.exists():
        raise FileNotFoundError(f"menu JSON file not found: {json_path}")

    db_url = _get_db_url()
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    items = _load_menu_items(json_path)

    with SessionLocal() as session:
        if args.truncate:
            session.query(MenuItem).delete()  # ok for dev; use TRUNCATE for large tables
            session.commit()

        ins, upd = _upsert_by_name(session, items)
        session.commit()

    print(f"Imported {len(items)} items → inserted={ins}, updated={upd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())