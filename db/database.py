from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.settings import get_database_url  # импортируем из settings

DATABASE_URL = get_database_url()  # получаем DATABASE_URL из .env

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
