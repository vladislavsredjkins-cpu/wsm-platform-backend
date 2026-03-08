from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db.base import Base

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if not DATABASE_URL:
    raise RuntimeError(f"DATABASE_URL is not set. Expected .env at: {BASE_DIR / '.env'}")

ASYNC_DATABASE_URL = DATABASE_URL
if ASYNC_DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1,
    )

if "ssl=" not in ASYNC_DATABASE_URL and "sslmode=" not in ASYNC_DATABASE_URL:
    separator = "&" if "?" in ASYNC_DATABASE_URL else "?"
    ASYNC_DATABASE_URL = f"{ASYNC_DATABASE_URL}{separator}ssl=require"

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
