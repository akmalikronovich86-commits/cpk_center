FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем pip с увеличенным таймаутом и зеркалом
RUN pip config set global.timeout 300 && \
    pip config set global.retries 5 && \
    pip config set global.index-url https://pypi.org/simple/

COPY requirements.txt .

# Устанавливаем зависимости с увеличенным таймаутом
RUN pip install Pillow==10.4.0 --no-cache-dir --default-timeout=300 --retries=5 -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
