# Система обнаружения изменений в документах с проверкой соответствия нормативам

## Описание проекта

Данная система предназначена для автоматического обнаружения изменений в документах и проверки их соответствия нормативным требованиям. Система использует технологии искусственного интеллекта для анализа изменений и генерации актов разногласий.

## Архитектура

Система построена на микросервисной архитектуре:
- **Frontend**: React + TypeScript + Vite, контейнеризованный с Nginx
- **Backend**: Python FastAPI для обработки документов и API
- **Database**: PostgreSQL для хранения нормативных документов и результатов анализа
- **LLM Integration**: Self Hosted LLM с OpenAI SDK для интеллектуального анализа изменений

## Функциональность

- Загрузка и сравнение документов (эталон и экземпляр клиента)
- Автоматическое обнаружение изменений на уровне абзацев
- Сопоставление изменений с нормативными документами
- LLM-анализ для определения необходимых согласований
- Генерация актов разногласий с детальными комментариями
- Экспорт результатов в различных форматах

## Быстрый старт

### Требования

- Docker и Docker Compose
- Не менее 4GB свободной оперативной памяти

### Установка

1. Клонирование репозитория:
```bash
git clone git@github.com:Skorp321/detecting_changes_in_a_document.git
cd detecting_changes_in_a_document
```

2. Создание файла окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл, добавив необходимые API ключи
```

3. Запуск системы:
```bash
docker compose up -d
```

4. Инициализация базы данных:
```bash
docker compose exec backend python -m app.database.init_db
```

### Доступ к системе

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Database: localhost:5432

## Использование

### Загрузка документов

1. Откройте веб-интерфейс по адресу http://localhost:3000
2. Загрузите эталонный документ в первое поле
3. Загрузите экземпляр клиента во второе поле
4. Нажмите "Анализировать изменения"

### Поддерживаемые форматы

- Microsoft Word (.docx)
- PDF (.pdf)
- Текстовые файлы (.txt)

### Результаты анализа

Система выводит результаты в виде таблицы с колонками:
- **Оригинальный текст**: Текст из эталонного документа
- **Измененный текст**: Текст из экземпляра клиента
- **Комментарии LLM**: Анализ изменений от AI
- **Необходимые согласования**: Список служб для согласования

## API Документация

### Основные endpoints

#### POST /api/compare
Сравнение двух документов и анализ изменений.

**Request:**
```
Content-Type: multipart/form-data
```
- `reference_doc`: Файл эталонного документа
- `client_doc`: Файл экземпляра клиента

**Response:**
```json
{
  "analysis_id": "uuid",
  "changes": [
    {
      "original_text": "Оригинальный текст",
      "modified_text": "Измененный текст",
      "llm_comment": "Комментарий анализа",
      "required_services": ["Юридическая служба", "Служба комплаенс"]
    }
  ],
  "summary": {
    "total_changes": 5,
    "critical_changes": 1,
    "processing_time": "2.5s"
  }
}
```

#### GET /api/health
Проверка состояния системы.

#### GET /api/regulations
Получение списка нормативных документов.

## Переменные окружения

| Переменная | Описание | Обязательна |
|------------|----------|-------------|
| `POSTGRES_HOST` | Хост базы данных | Да |
| `POSTGRES_USER` | Пользователь БД | Да |
| `POSTGRES_PASSWORD` | Пароль БД | Да |
| `POSTGRES_DB` | Название БД | Да |
| `OPENAI_API_KEY` | API ключ OpenAI | Да |
| `OPENAI_MODEL` | Модель OpenAI | Нет |
| `MAX_FILE_SIZE` | Макс. размер файла | Нет |
| `ALLOWED_EXTENSIONS` | Разрешенные расширения | Нет |

## Разработка

### Структура проекта

```
oozo/
├── frontend/           # React приложение
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── Dockerfile
├── backend/           # Python FastAPI
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   └── schemas/
│   ├── requirements.txt
│   └── Dockerfile
├── db/               # SQL скрипты
└── tests/           # Тесты
```

### Локальная разработка

1. Запуск только БД:
```bash
docker-compose up -d postgres
```

2. Запуск backend локально:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Запуск frontend локально:
```bash
cd frontend
npm install
npm run dev
```

### Тестирование

```bash
# Запуск всех тестов
docker-compose exec backend pytest

# Запуск конкретного теста
docker-compose exec backend pytest tests/test_document_processor.py

# Запуск с покрытием кода
docker-compose exec backend pytest --cov=app
```

### Линтинг и форматирование

```bash
# Backend
docker-compose exec backend black app/
docker-compose exec backend isort app/

# Frontend
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run format
```

## Устранение неполадок

### Общие проблемы

1. **Контейнеры не запускаются**
   - Проверьте, что Docker daemon запущен
   - Убедитесь, что порты 3000, 8000, 5432 свободны

2. **Ошибки базы данных**
   - Проверьте переменные окружения
   - Убедитесь, что база данных инициализирована

3. **Ошибки LLM анализа**
   - Проверьте правильность OPENAI_API_KEY
   - Убедитесь в наличии средств на аккаунте OpenAI

4. **Проблемы с обработкой файлов**
   - Проверьте формат и размер файлов
   - Убедитесь, что файлы не повреждены

### Логи

```bash
# Просмотр логов всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

## Вклад в проект

1. Форк репозитория
2. Создание feature branch
3. Внесение изменений с тестами
4. Создание Pull Request

## Лицензия

MIT License

## Поддержка

Для получения поддержки создайте Issue в репозитории или обратитесь к документации API. 
