from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# SQLite compatibility code has been removed.
# Every Alembic migration after 0001 requires PostgreSQL.
# If DATABASE_URL is not set, Settings raises a ValidationError at startup.
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
