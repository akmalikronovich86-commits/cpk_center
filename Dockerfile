FROM python:3.12-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    gettext \
    libfreetype6-dev \
    libfontconfig1-dev \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем pip
RUN pip config set global.timeout 300 && \
    pip config set global.retries 5 && \
    pip config set global.index-url https://pypi.org/simple/

COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --default-timeout=300 --retries=5 -r requirements.txt

COPY . .

# Создаём директорию для логов
RUN mkdir -p /app/logs

# Собираем статику
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Production сервер (Gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "cpk_center.wsgi:application"]
