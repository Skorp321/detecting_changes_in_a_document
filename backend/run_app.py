#!/usr/bin/env python3
"""
Скрипт для запуска приложения OOZO с переменными по умолчанию
"""

import os
import sys
from pathlib import Path

# Устанавливаем переменные окружения по умолчанию
os.environ.setdefault('OPENAI_API_KEY', 'dummy_key_for_testing')
os.environ.setdefault('OPENAI_BASE_URL', 'https://10f9698e-46b7-4a33-be37-f6495989f01f.modelrun.inference.cloud.ru')
os.environ.setdefault('OPENAI_MODEL', 'qwen3:32b')
os.environ.setdefault('OPENAI_TEMPERATURE', '0.3')
os.environ.setdefault('OPENAI_MAX_TOKENS', '2000')
os.environ.setdefault('FAISS_INDEX_PATH', str(Path(__file__).parent / 'faiss_index'))
os.environ.setdefault('UPLOAD_PATH', str(Path(__file__).parent / 'uploads'))
os.environ.setdefault('LOG_FILE', str(Path(__file__).parent / 'logs' / 'app.log'))
os.environ.setdefault('DEBUG', 'true')
os.environ.setdefault('HOST', '0.0.0.0')
os.environ.setdefault('PORT', '8000')
os.environ.setdefault('WORKERS', '1')
os.environ.setdefault('RELOAD', 'true')
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('MAX_FILE_SIZE', '10485760')
os.environ.setdefault('ALLOWED_EXTENSIONS', 'pdf,docx,txt')
os.environ.setdefault('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')
os.environ.setdefault('ALLOWED_HOSTS', '*')
os.environ.setdefault('SECRET_KEY', 'your_secret_key_here_change_in_production')
os.environ.setdefault('ALGORITHM', 'HS256')
os.environ.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', '30')
os.environ.setdefault('MAX_DOCUMENT_PAGES', '50')
os.environ.setdefault('PROCESSING_TIMEOUT', '300')
os.environ.setdefault('CHUNK_SIZE', '1000')
os.environ.setdefault('ANALYSIS_BATCH_SIZE', '10')
os.environ.setdefault('RETRY_ATTEMPTS', '3')
os.environ.setdefault('RATE_LIMIT_REQUESTS', '100')
os.environ.setdefault('RATE_LIMIT_WINDOW', '60')
os.environ.setdefault('FAISS_DIMENSION', '1536')
os.environ.setdefault('FAISS_METRIC', 'cosine')
os.environ.setdefault('FORCE_REBUILD_FAISS', 'true')  # Пересоздавать FAISS индекс при каждом запуске
os.environ.setdefault('LANGCHAIN_TRACING_V2', 'false')
os.environ.setdefault('LANGCHAIN_ENDPOINT', '')
os.environ.setdefault('LANGCHAIN_API_KEY', '')
os.environ.setdefault('LANGCHAIN_PROJECT', 'oozo')

# Добавляем текущую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent))

# Создаем необходимые директории
os.makedirs(os.environ['FAISS_INDEX_PATH'], exist_ok=True)
os.makedirs(os.environ['UPLOAD_PATH'], exist_ok=True)
os.makedirs(Path(os.environ['LOG_FILE']).parent, exist_ok=True)

if __name__ == "__main__":
    # Импортируем и запускаем приложение
    from app.main import app
    import uvicorn
    
    print("Запуск приложения OOZO...")
    print(f"FAISS индекс: {os.environ['FAISS_INDEX_PATH']}")
    print(f"Загрузки: {os.environ['UPLOAD_PATH']}")
    print(f"Логи: {os.environ['LOG_FILE']}")
    
    uvicorn.run(
        app,
        host=os.environ['HOST'],
        port=int(os.environ['PORT']),
        reload=os.environ['RELOAD'].lower() == 'true',
        workers=int(os.environ['WORKERS']),
        log_level=os.environ['LOG_LEVEL'].lower()
    )


