import json
import sys
from pathlib import Path
from sqlalchemy import text

# --- PATH CONFIGURATION ---
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "src"))

from app.database import SessionLocal
from app.models.user import User
from app.models.table import Table
from app.models.menu_item import MenuItem
from app.api.deps.auth import hash_password

def seed_database():
    db = SessionLocal()
    print("\n" + "═"*50)
    print("🧨 NUKING DATABASE (TRUNCATE + RESTART IDENTITY)")
    print("═"*50)
    
    # Tables to wipe in order of dependency
    tables_to_wipe = [
        "seat_assignments", "order_items", "orders", 
        "reservation_attendees", "reservations", "menu_items", 
        "tables", "messages", "revoked_tokens", "users"
    ]
    
    try:
        for table in tables_to_wipe:
            # CASCADE drops rows and resets SERIAL IDs to 1
            db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
        db.commit()
        print("✅ Tables truncated and IDs reset.")
    except Exception as e:
        print(f"⚠️  Truncate warning: {e}")
        db.rollback()

    # --- SEED USERS ---
    print("\n🌱 Seeding Admin User...")
    # This matches your app/models/user.py exactly
    admin = User(
        email="josh@josh.com",
        password_hash=hash_password("1111"),
        role="admin"
    )
    db.add(admin)

    # --- SEED TABLES ---
    print("🌱 Seeding Dining Rooms & Tables...")
    dr_path = ROOT_DIR / "data" / "dining_rooms.json"
    if dr_path.exists():
        with open(dr_path) as f:
            rooms_data = json.load(f)
            for entry in rooms_data:
                db.add(Table(
                    dining_room=entry["dining_room"],
                    name=entry["name"],
                    seat_count=entry["seat_count"]
                ))
    
    # --- SEED MENU ---
    print("🌱 Seeding Menu Items...")
    menu_path = ROOT_DIR / "data" / "menu.json"
    if menu_path.exists():
        with open(menu_path) as f:
            menu_data = json.load(f)
            for item in menu_data:
                db.add(MenuItem(**item))

    db.commit()
    db.close()
    print("\n" + "═"*50)
    print("✅ DATABASE IS FRESH AND SEEDED.")
    print("═"*50 + "\n")

if __name__ == "__main__":
    seed_database()