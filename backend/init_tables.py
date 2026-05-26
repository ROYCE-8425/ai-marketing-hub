from core.database import engine
from core.models import Base
Base.metadata.create_all(engine)
print("All tables created successfully")
