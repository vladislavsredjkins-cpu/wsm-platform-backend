from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://wsm_platform_db_user:W7nVn4hO1rl4SDdFRCFA8QhahJt1DHxH@dpg-d6kq2lvpm1nc73f4v040-a.frankfurt-postgres.render.com/wsm_platform_db"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
