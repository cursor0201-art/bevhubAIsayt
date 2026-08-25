# Используем официальный образ Python 3.12
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Запрещаем Python писать .pyc файлы и буферизовать stdout
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код бэкенда
COPY . /app/

# Открываем порт
EXPOSE 8000

# Скрипт запуска: сначала миграции, потом сервер
RUN echo '#!/bin/bash\nset -e\npython manage.py migrate --noinput\npython manage.py collectstatic --noinput\nexec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
