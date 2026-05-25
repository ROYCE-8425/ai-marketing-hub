import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Lấy DATABASE_URL từ biến môi trường. Mặc định là chuỗi rỗng để tránh lỗi nếu quên set.
# Đối với PostgreSQL chạy qua Docker: postgresql://amh_user:amh_password@postgres:5432/aimarketinghub
# (hoặc localhost:5432 nếu chạy từ bên ngoài host)
# 
# FALLBACK: Nếu không có cấu hình PostgreSQL, fallback tạm thời sang SQLite duy nhất.
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'amh_database.db')}"
)

# Khởi tạo SQLAlchemy Engine
# Lưu ý: connect_args={"check_same_thread": False} chỉ cần cho SQLite
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args,
    # echo=True  # Bật dòng này lên nếu muốn in ra SQL raw log
)

# Tạo SessionLocal class để quản lý database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho tất cả các SQLAlchemy models
Base = declarative_base()

# Dependency để sử dụng trong FastAPI (Yields a session)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
