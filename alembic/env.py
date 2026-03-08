import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context

from db.model_registry import target_metadata


# --------------------------------
# LOAD ENV VARIABLES
# --------------------------------

load_dotenv()

# --------------------------------
# ALEMBIC CONFIG
# --------------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --------------------------------
# DATABASE URL
# --------------------------------

db_url = os.getenv("DATABASE_URL")

if not db_url:
    raise RuntimeError("DATABASE_URL is not set")

# Alembic работает через sync драйвер
sync_db_url = db_url.replace(
    "postgresql+asyncpg://",
    "postgresql+psycopg2://"
)

config.set_main_option("sqlalchemy.url", sync_db_url)


# --------------------------------
# OFFLINE MIGRATIONS
# --------------------------------

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


# --------------------------------
# ONLINE MIGRATIONS
# --------------------------------

def run_migrations_online():
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url")
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# --------------------------------
# ENTRYPOINT
# --------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
