import json
import sys
from pathlib import Path
from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from app.database import SessionLocal
from app.models.user import User
from app.models.member import Member
from app.models.table import Table
from app.models.menu_item import MenuItem
from app.models.dining_room import DiningRoom
from app.api.deps.auth import hash_password

def seed():
    db = SessionLocal()
    print("🧨 NUKING DATABASE...")
    tables = ["order_items", "orders", "menu_items", "tables", "dining_rooms", "members", "users"]
    
    try:
        for table in tables:
            db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
        db.commit()

        # 1. ADMIN
        admin = User(email="josh@josh.com", password_hash=hash_password("1111"), role="admin", is_active=True)
        db.add(admin)
        db.flush()
        db.add(Member(user_id=admin.id, name="Josh Dicker", relation="Primary"))
        print(f"✅ Admin Created (ID: {admin.id})")

        # 2. DINING ROOMS
        dr_path = ROOT_DIR / "scripts" / "data" / "dining_rooms.json"
        if dr_path.exists():
            with open(dr_path) as f:
                rooms_data = json.load(f)
            
            room_map = {}
            for entry in rooms_data:
                r_name = entry["dining_room"]
                if r_name not in room_map:
                    dr = DiningRoom(name=r_name, is_active=True)
                    db.add(dr)
                    db.flush()
                    room_map[r_name] = dr.id
                    print(f"✅ Created Room: {r_name}")

                t = Table(name=entry["name"], seat_count=entry["seat_count"], dining_room_id=room_map[r_name])
                db.add(t)
            print(f"✅ Tables seeded.")
        else:
            print("⚠️ Skipping Rooms: dining_rooms.json NOT FOUND")

        # 3. MENU
        m_path = ROOT_DIR / "scripts" / "data" / "menu.json"
        if m_path.exists():
            with open(m_path) as f:
                menu_data = json.load(f)
            for item in menu_data:
                mi = MenuItem(**item)
                db.add(mi)
            print(f"✅ Seeded {len(menu_data)} Menu Items.")
        else:
            print("⚠️ Skipping Menu: menu.json NOT FOUND")

        db.commit()
        print("🔥 ALL DATA COMMITTED SUCCESSFULLY.")

    except Exception as e:
        print(f"❌ SEED FAILED: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()