FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание пользователя для безопасности
RUN useradd -m -u 1000 streamlit && chown -R streamlit:streamlit /app
USER streamlit

# Экспорт порта
EXPOSE 8501

# Переменные окружения
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Команда запуска
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

