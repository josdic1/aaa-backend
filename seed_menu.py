# seed_menu.py
import json
import os
import sys

# Ensures the current directory is in the path so 'from app...' works
sys.path.insert(0, os.path.abspath(os.curdir))

from app.database import SessionLocal
from app.models.menu_item import MenuItem

def seed():
    # Use context manager to ensure DB closure
    db = SessionLocal()
    try:
        # Check if JSON exists
        if not os.path.exists("menu.json"):
            print("Error: menu.json not found!")
            return

        with open("menu.json") as f:
            items = json.load(f)

        for item in items:
            # item is a dict, **item unpacks it into MenuItem columns
            db.add(MenuItem(**item))
        
        db.commit()
        print(f"Successfully seeded {len(items)} menu items.")
    except Exception as e:
        db.rollback()
        print(f"FAILED: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()