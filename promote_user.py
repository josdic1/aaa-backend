# promote_user.py
import sys
import os

# Ensure the script can find the 'app' directory
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models.user import User

def promote(email: str):
    # Use the session you already configured in app.database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User {email} not found.")
            return

        # Explicitly set the role to admin
        user.role = "admin"
        
        db.commit()
        print(f"✅ Success: {email} is now an admin.")
        
    except Exception as e:
        db.rollback()
        print(f"🔥 Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python promote_user.py <email>")
    else:
        promote(sys.argv[1])