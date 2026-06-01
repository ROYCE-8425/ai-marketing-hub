"""Create trannhuy8425@gmail.com as admin (Google OAuth user)."""
from core.database import SessionLocal
from core.models import User

db = SessionLocal()

# Check if already exists
u = db.query(User).filter(User.email == "trannhuy8425@gmail.com").first()
if u:
    u.role = "admin"
    db.commit()
    print(f"Updated existing user {u.email} to admin")
else:
    # Create as Google OAuth user (no password)
    new_user = User(
        email="trannhuy8425@gmail.com",
        full_name="Tran Nhu Y",
        hashed_password="GOOGLE_OAUTH",
        role="admin",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    print(f"Created admin user: trannhuy8425@gmail.com")

# Show all users
print("\nAll users:")
for x in db.query(User).all():
    print(f"  {x.id}: {x.email} | role={x.role} | active={x.is_active}")

db.close()
