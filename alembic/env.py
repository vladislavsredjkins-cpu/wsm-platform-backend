import sys
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

from db.model_registry import target_metadata
import os

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    raise RuntimeError(f"DATABASE_URL is not set. Expected .env at: {BASE_DIR / '.env'}")

SYNC_DATABASE_URL = DATABASE_URL
if SYNC_DATABASE_URL.startswith("postgresql://"):
    SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg2://",
        1,
    )
elif SYNC_DATABASE_URL.startswith("postgresql+asyncpg://"):
    SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace(
        "postgresql+asyncpg://",
        "postgresql+psycopg2://",
        1,
    )

if "sslmode=" not in SYNC_DATABASE_URL:
    separator = "&" if "?" in SYNC_DATABASE_URL else "?"
    SYNC_DATABASE_URL = f"{SYNC_DATABASE_URL}{separator}sslmode=require"

config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(config.get_main_option("sqlalchemy.url"))

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
