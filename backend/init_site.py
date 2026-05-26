from core.database import SessionLocal
from core.models import ManagedSite, User
from core.auth import hash_password

db = SessionLocal()

# Get or create admin user
admin = db.query(User).filter(User.email == "admin@aimarketing.vn").first()
if not admin:
    admin = User(
        email="admin@aimarketing.vn",
        full_name="Admin",
        hashed_password=hash_password("admin123"),
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"Admin user created with id={admin.id}")
else:
    print(f"Admin user exists with id={admin.id}")

# Add site
existing = db.query(ManagedSite).filter(ManagedSite.url == "https://binhphuocmitsubishi.com").first()
if not existing:
    site = ManagedSite(
        user_id=admin.id,
        name="Mitsubishi Binh Phuoc",
        url="https://binhphuocmitsubishi.com",
        description="Dai ly Mitsubishi Binh Phuoc",
        niche="o to",
        is_active=True,
    )
    db.add(site)
    db.commit()
    print(f"Site added with id={site.id}")
else:
    print(f"Site already exists with id={existing.id}")

db.close()
