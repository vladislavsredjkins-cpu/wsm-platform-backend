FROM python:3.11-slim

WORKDIR /app

# Скопировать зависимости и установить
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Скопировать код
COPY backend /app/backend

# Render прокидывает PORT, поэтому запускаем через shell
CMD sh -c "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"
