# core/settings.py
import os
from dotenv import load_dotenv

load_dotenv()  # Загрузка переменных из .env

def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL", "").strip()

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    return database_url
