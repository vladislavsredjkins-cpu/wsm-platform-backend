# core/settings.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Загружаем .env
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Получаем DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Если база не настроена, выбрасываем ошибку
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")
