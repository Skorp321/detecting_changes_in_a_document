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
# База данных инициализируется автоматически при первом запуске
docker compose logs postgres  # Проверить статус инициализации
```

5. Доступ к приложению:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API документация: http://localhost:8000/docs

## Оптимизация производительности

### Настройки Nginx

Система использует оптимизированную конфигурацию Nginx с:
- Brotli и Gzip сжатием для статических файлов
- Предварительным сжатием файлов при сборке
- Кэшированием статических ресурсов на 1 год
- Security headers для защиты от XSS и других атак

### Разделение JavaScript chunks

Vite настроен для оптимального разделения кода:
- `vendor` - основные React библиотеки
- `antd` - компоненты UI
- `pdf` - обработка PDF файлов
- `utils` - утилитарные библиотеки (lodash, dayjs)
- `ui` - дополнительные UI компоненты

### Lazy Loading компонентов

Основные компоненты загружаются по требованию:
- DocumentUpload - загрузка документов
- ResultsTable - таблица результатов
- AnalysisButton - кнопка анализа

## Мониторинг

### Запуск системы мониторинга

```bash
# Запуск основной системы
docker-compose up -d

# Запуск мониторинга
docker-compose -f monitoring/docker-compose.monitoring.yml up -d
```

### Доступ к мониторингу

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

### Web Vitals метрики

Система автоматически собирает Web Vitals метрики:
- **LCP** (Largest Contentful Paint) - время загрузки основного контента
- **FID** (First Input Delay) - время отклика на первое взаимодействие
- **CLS** (Cumulative Layout Shift) - стабильность макета
- **FCP** (First Contentful Paint) - время до первого контента
- **TTFB** (Time to First Byte) - время до первого байта

### Алерты

Настроены алерты для:
- Время отклика > 5 секунд
- Недоступность сервисов > 2 минут
- Высокая загрузка CPU > 80%
- Высокое потребление памяти > 90%
- Плохие Web Vitals метрики

## Анализ производительности

### Анализ размера bundle

```bash
cd frontend
npm run analyze
```

### Тестирование производительности

```bash
# Запуск нагрузочного тестирования
docker-compose exec backend python -m pytest tests/performance/ -v

# Проверка Web Vitals
# Откройте DevTools > Lighthouse > Generate report
```

### Мониторинг в реальном времени

```bash
# Логи системы
docker-compose logs -f

# Метрики из Prometheus
curl http://localhost:9090/api/v1/query?query=up

# Статус сервисов
curl http://localhost:3000/health
curl http://localhost:8000/api/health
```

## Troubleshooting

### Проблемы с производительностью

1. **Медленная загрузка страницы**:
   - Проверьте сжатие файлов: `curl -H "Accept-Encoding: gzip,br" -I http://localhost:3000`
   - Проверьте кэширование: headers должны содержать `Cache-Control: public, immutable`

2. **Высокое потребление памяти**:
   - Проверьте метрики в Grafana
   - Перезапустите контейнеры: `docker-compose restart`

3. **Медленный API**:
   - Проверьте логи backend: `docker-compose logs backend`
   - Проверьте соединение с БД: `docker-compose exec postgres pg_isready`

### Проблемы с мониторингом

1. **Prometheus не собирает метрики**:
   - Проверьте статус targets: http://localhost:9090/targets
   - Проверьте сетевую связность между контейнерами

2. **Grafana не показывает данные**:
   - Проверьте подключение к Prometheus в Data Sources
   - Проверьте запросы в Query Inspector

## Deployment

### Production развертывание

1. Обновите переменные окружения:
```bash
# .env
VITE_ENABLE_WEB_VITALS=true
POSTGRES_PASSWORD=secure_password
# ... другие production настройки
```

2. Используйте production конфигурацию:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

3. Настройте SSL/TLS:
```bash
# Добавьте reverse proxy с SSL
# Например, с помощью Traefik или Nginx
```

### Автоматическое развертывание

```bash
# CI/CD pipeline пример
#!/bin/bash
docker-compose down
docker-compose pull
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
```

### Резервное копирование

```bash
# Backup базы данных
docker-compose exec postgres pg_dump -U oozo_user oozo > backup.sql

# Backup мониторинга
docker-compose exec prometheus promtool tsdb snapshot /prometheus

# Restore
docker-compose exec postgres psql -U oozo_user oozo < backup.sql
```
```bash
docker-compose exec backend python -m app.database.init_db
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
