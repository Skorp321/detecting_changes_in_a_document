#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы Streamlit приложения
"""

import requests
import json
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def test_api_connection():
    """Тестирование подключения к API"""
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    print("🔍 Тестирование подключения к API...")
    print(f"URL: {api_url}")
    
    try:
        # Тест health endpoint
        response = requests.get(f"{api_url}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ API доступен")
            health_data = response.json()
            print(f"   Статус: {health_data.get('status', 'N/A')}")
            print(f"   Версия: {health_data.get('version', 'N/A')}")
            return True
        else:
            print(f"❌ API недоступен. Код ответа: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения к API")
        print("   Убедитесь, что API сервер запущен")
        return False
    except requests.exceptions.Timeout:
        print("❌ Таймаут подключения к API")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")
        return False

def test_regulations_endpoint():
    """Тестирование endpoint для получения нормативных документов"""
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    print("\n📋 Тестирование endpoint нормативных документов...")
    
    try:
        response = requests.get(f"{api_url}/regulations", timeout=5)
        
        if response.status_code == 200:
            regulations = response.json()
            print(f"✅ Получено {len(regulations)} нормативных документов")
            return True
        else:
            print(f"❌ Ошибка получения нормативных документов. Код: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False

def test_services_endpoint():
    """Тестирование endpoint для получения служб"""
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    print("\n🏢 Тестирование endpoint служб...")
    
    try:
        response = requests.get(f"{api_url}/services", timeout=5)
        
        if response.status_code == 200:
            services = response.json()
            print(f"✅ Получено {len(services)} служб")
            return True
        else:
            print(f"❌ Ошибка получения служб. Код: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False

def main():
    """Главная функция тестирования"""
    print("🧪 Тестирование Streamlit приложения для анализа документов")
    print("=" * 60)
    
    # Проверяем наличие файла конфигурации
    if not os.path.exists(".env"):
        print("⚠️  Файл .env не найден")
        print("   Скопируйте env_example.txt в .env и настройте API URL")
        return
    
    # Тестируем подключение к API
    api_ok = test_api_connection()
    
    if api_ok:
        # Тестируем дополнительные endpoints
        test_regulations_endpoint()
        test_services_endpoint()
        
        print("\n✅ Все тесты пройдены успешно!")
        print("🚀 Приложение готово к использованию")
        print("   Запустите: streamlit run app.py")
    else:
        print("\n❌ Тесты не пройдены")
        print("   Проверьте настройки API в файле .env")
        print("   Убедитесь, что API сервер запущен")

if __name__ == "__main__":
    main()


