import os
import sys
import socket
from pathlib import Path

# Path setup 
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

def check_venv_integrity():
    is_venv = sys.prefix != sys.base_prefix or "VIRTUAL_ENV" in os.environ
    print("🛡️  VENV CHECK")
    if not is_venv:
        print("   ❌ CRITICAL: Running in Global Python!")
        sys.exit(1)
    print(f"   ✅ Venv Active: {sys.prefix}")

def check_infrastructure():
    print("\n🐘 INFRASTRUCTURE")
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("   ⚠️  DATABASE_URL: Missing")
    else:
        try:
            host_part = db_url.split("@")[-1].split("/")[0]
            host = host_part.split(":")[0]
            port = int(host_part.split(":")[1]) if ":" in host_part else 5432
            socket.create_connection((host, port), timeout=1)
            print(f"   Postgres: 🟢 Online ({host})")
        except Exception:
            print("   Postgres: 🔴 Offline")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', 8080)) == 0:
            print("   Port 8080: 🚫 BUSY")
        else:
            print("   Port 8080: 🟢 AVAILABLE")

def generate_debug_token():
    """Generates the token using the User ID (Integer) as the subject."""
    if "--token" in sys.argv:
        try:
            from app.api.deps.auth import create_access_token
            from app.database import SessionLocal
            from app.models.user import User
            
            db = SessionLocal()
            # Find Josh to get his ID
            user = db.query(User).filter(User.email == "josh@josh.com").first()
            db.close()

            if not user:
                print("🔑 Auth Error: User josh@josh.com not found. Check your DB!")
                return

            # CRITICAL: Your auth.py does 'user_id = int(sub)'. 
            # We must pass the ID as a string.
            token = create_access_token(subject=str(user.id))
            print(f"TOKEN_START:{token}:TOKEN_END")
        except Exception as e:
            print(f"🔑 Auth Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*50)
    check_venv_integrity()
    check_infrastructure()
    generate_debug_token()
    print("="*50 + "\n")