from core.database import SessionLocal
from core.models import User

db = SessionLocal()

# Set trannhuy8425@gmail.com as admin
u = db.query(User).filter(User.email == "trannhuy8425@gmail.com").first()
if u:
    u.role = "admin"
    db.commit()
    print(f"Updated {u.email} to admin")
else:
    print("User trannhuy8425@gmail.com not found")

# List all users
print("\nAll users:")
for x in db.query(User).all():
    print(f"  {x.id}: {x.email} | role={x.role} | active={x.is_active}")

db.close()
