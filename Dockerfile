FROM python:3.11-slim

WORKDIR /app

# Скопировать зависимости
COPY backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Скопировать backend
COPY backend/ ./backend/

# Запуск FastAPI
CMD ["sh", "-c", "uvicorn main:app --app-dir backend --host 0.0.0.0 --port $PORT"]
