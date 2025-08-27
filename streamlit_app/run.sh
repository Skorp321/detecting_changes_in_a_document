#!/bin/bash

# Скрипт для запуска Streamlit приложения

echo "🚀 Запуск Streamlit приложения для анализа документов..."

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

# Проверка наличия pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден. Установите pip"
    exit 1
fi

# Создание виртуального окружения (если не существует)
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📚 Установка зависимостей..."
pip install -r requirements.txt

# Проверка наличия файла .env
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден. Создаю из примера..."
    cp env_example.txt .env
    echo "📝 Отредактируйте файл .env для настройки API URL"
fi

# Запуск приложения
echo "🌐 Запуск Streamlit приложения..."
echo "📱 Приложение будет доступно по адресу: http://localhost:8501"
echo "🛑 Для остановки нажмите Ctrl+C"

streamlit run app.py --server.port=8501 --server.address=0.0.0.0

