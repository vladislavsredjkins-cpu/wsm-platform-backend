import os
import sys
from pathlib import Path
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import create_engine
from alembic import context

from core.settings import DATABASE_URL  # Извлекаем из настроек

config.set_main_option("sqlalchemy.url", DATABASE_URL)

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

from db.model_registry import target_metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

db_url = os.getenv("DATABASE_URL", "").strip()
if not db_url:
    raise RuntimeError(
        f"DATABASE_URL is not set. Expected .env at: {BASE_DIR / '.env'}"
    )

sync_db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
config.set_main_option("sqlalchemy.url", sync_db_url)


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
