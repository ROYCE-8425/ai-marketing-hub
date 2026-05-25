"""
AI Marketing Hub — Unified PostgreSQL Database Initializer
==========================================================
Tạo các bảng theo cấu trúc SQLAlchemy Models (models.py) và tự động
thêm dữ liệu mẫu vào cơ sở dữ liệu.
"""

import os
import sys
import random
from datetime import datetime, timedelta

# Import từ thư mục hiện tại
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import engine, Base, SessionLocal
from core.models import User, ManagedSite, TrackedKeyword, RankingHistory, ContentItem, AbTest

def log(msg: str):
    print(f"  ✅ {msg}")

def warn(msg: str):
    print(f"  ⚠️  {msg}")

def header(msg: str):
    print(f"\n{'─' * 60}")
    print(f"  📦 {msg}")
    print(f"{'─' * 60}")

def init_database():
    print("=" * 60)
    print("  🚀 AI Marketing Hub — Unified DB Initializer")
    print("=" * 60)
    
    # 1. Tạo tất cả các bảng
    header("Tạo Database Schema...")
    Base.metadata.create_all(bind=engine)
    log("Đã tạo thành công tất cả các bảng từ models.py")

    db = SessionLocal()
    
    try:
        # 2. Tạo Admin User mặc định
        header("Tạo Admin User")
        admin_email = "admin@aimarketing.vn"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            try:
                import bcrypt
                hashed = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            except ImportError:
                import hashlib
                hashed = hashlib.sha256("admin123".encode()).hexdigest()
                warn("bcrypt not found, using SHA256 fallback for admin password")

            admin_user = User(
                email=admin_email,
                full_name="Admin",
                hashed_password=hashed,
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            log("Created default admin: admin@aimarketing.vn / admin123")
        else:
            warn("Admin user already exists, skipping")

        # 3. Tạo Sample Site
        header("Tạo Managed Site")
        site_url = "https://binhphuocmitsubishi.com"
        site = db.query(ManagedSite).filter(ManagedSite.url == site_url).first()
        if not site:
            site = ManagedSite(
                user_id=admin_user.id,
                name="Mitsubishi Bình Phước",
                url=site_url,
                description="Đại lý chính hãng Mitsubishi tại Bình Phước",
                niche="ô tô",
                is_active=True,
                last_scan_score=78,
                last_scan_date=datetime.now()
            )
            db.add(site)
            db.commit()
            db.refresh(site)
            log("Inserted default site: binhphuocmitsubishi.com")
        else:
            warn("Default site already exists, skipping")

        # 4. Tạo Sample Keywords
        header("Tạo Sample Keywords & History")
        existing_keywords = db.query(TrackedKeyword).filter(TrackedKeyword.site_id == site.id).count()
        if existing_keywords == 0:
            keywords_data = [
                ("mitsubishi bình phước", "thương hiệu"),
                ("giá xe xpander 2026", "sản phẩm"),
                ("mitsubishi xpander bình phước", "thương hiệu"),
                ("đại lý mitsubishi bình phước", "thương hiệu"),
                ("xe pajero sport giá tốt", "sản phẩm"),
                ("mua xe trả góp bình phước", "dịch vụ"),
                ("so sánh xpander và rush", "so sánh"),
                ("bảo dưỡng xe mitsubishi", "dịch vụ"),
                ("xe attrage 2026 giá bao nhiêu", "sản phẩm"),
                ("lái thử xe mitsubishi", "dịch vụ"),
            ]
            
            now = datetime.now()
            history_records = []
            
            for kw_text, tag in keywords_data:
                kw = TrackedKeyword(site_id=site.id, keyword=kw_text, tag=tag)
                db.add(kw)
                db.flush() # Lấy ID
                
                # Generate history
                base_pos = random.uniform(3, 25)
                for day_offset in range(30, -1, -1):
                    date_val = now - timedelta(days=day_offset)
                    pos = max(1, base_pos + random.uniform(-3, 3))
                    clicks = max(0, int(random.gauss(15, 8)))
                    impressions = max(clicks, int(random.gauss(200, 80)))
                    ctr = round((clicks / impressions * 100) if impressions > 0 else 0, 2)
                    
                    history = RankingHistory(
                        tracked_keyword_id=kw.id,
                        position=round(pos, 1),
                        clicks=clicks,
                        impressions=impressions,
                        ctr=ctr,
                        source='sample',
                        checked_at=date_val
                    )
                    history_records.append(history)
                base_pos *= 0.92

            db.add_all(history_records)
            db.commit()
            log(f"Inserted {len(keywords_data)} keywords with {len(history_records)} history records.")
        else:
            warn("Rank tracker data already exists, skipping")

        # 5. Tạo Sample Content Items
        header("Tạo Sample Content Calendar")
        existing_content = db.query(ContentItem).filter(ContentItem.site_id == site.id).count()
        if existing_content == 0:
            now = datetime.now()
            samples = [
                ("Hướng dẫn mua xe Mitsubishi trả góp 2026", "blog", "published", -10, "mua xe trả góp"),
                ("So sánh Xpander vs Toyota Rush — Nên chọn xe nào?", "blog", "published", -5, "so sánh xpander rush"),
                ("Top 5 xe gia đình tốt nhất dưới 700 triệu", "blog", "scheduled", 3, "xe gia đình giá rẻ"),
                ("Bảng giá xe Mitsubishi tháng 6/2026", "page", "draft", 7, "bảng giá mitsubishi"),
                ("Review Pajero Sport 2026 — Có gì mới?", "blog", "idea", 14, "pajero sport 2026"),
                ("Chương trình khuyến mãi hè 2026", "promotion", "scheduled", 5, "khuyến mãi mitsubishi"),
            ]
            
            for title, ctype, status, day_offset, keyword in samples:
                date_str = (now + timedelta(days=day_offset)).strftime("%Y-%m-%d")
                published_str = date_str if status == "published" else None
                
                item = ContentItem(
                    site_id=site.id,
                    title=title,
                    content_type=ctype,
                    status=status,
                    scheduled_date=date_str,
                    published_date=published_str,
                    primary_keyword=keyword
                )
                db.add(item)
            db.commit()
            log(f"Inserted {len(samples)} sample content items")
        else:
            warn("Content calendar data already exists, skipping")

    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {str(e)}")
    finally:
        db.close()

    print(f"\n{'═' * 60}")
    print("  🎉 DATABASE INITIALIZATION COMPLETE!")
    print(f"{'═' * 60}")

if __name__ == "__main__":
    init_database()
