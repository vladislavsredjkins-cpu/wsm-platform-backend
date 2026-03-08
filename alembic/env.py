import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from alembic import context

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

SYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql+asyncpg",
    "postgresql+psycopg2",
    1
)

config = context.config
config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)
