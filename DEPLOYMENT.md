# Руководство по развертыванию

## Решение проблемы с загрузкой файлов

### Проблема
При локальном использовании приложения загрузка файлов работает корректно, но при развертывании в production возникает ошибка "Network Error".

### Причина
Frontend пытался обращаться к API по адресу `http://localhost:8000` вместо использования относительного пути `/api`, который правильно проксируется через nginx.

### Решение
1. В файле `frontend/src/services/api.ts` изменен baseURL с `http://localhost:8000` на `/api`
2. Обновлены все API пути, убрав дублирование `/api` префикса
3. Увеличен максимальный размер файла с 10MB до 50MB

## Настройка для production

### 1. Создайте файл .env на основе .env.example:
```bash
cp .env.example .env
```

### 2. Обновите настройки в .env:
- `POSTGRES_PASSWORD` - установите надежный пароль
- `CORS_ORIGINS` - добавьте домен вашего сайта
- `OPENAI_API_KEY` - добавьте ваш API ключ
- `SECRET_KEY` - установите уникальный секретный ключ

### 3. Важные настройки CORS:
Убедитесь, что в `CORS_ORIGINS` указаны все домены, с которых будет доступно приложение:
```
CORS_ORIGINS=http://localhost:3000,http://your-domain.com,https://your-domain.com
```

### 4. Запуск приложения:
```bash
docker-compose up -d
```

### 5. Проверка работоспособности:
- Frontend доступен по адресу: http://localhost:3000
- API health check: http://localhost:3000/api/health

## Ограничения

- Максимальный размер файла: 50MB
- Поддерживаемые форматы: PDF, DOCX, TXT
- Таймаут обработки: 5 минут

## Устранение неполадок

### Ошибка "Network Error" при загрузке файлов
1. Проверьте, что контейнеры запущены: `docker-compose ps`
2. Проверьте логи backend: `docker-compose logs backend`
3. Убедитесь, что CORS настроен правильно в .env файле

### Ошибка "413 Request Entity Too Large"
- Увеличьте `MAX_FILE_SIZE` в .env файле
- Убедитесь, что в nginx.conf `client_max_body_size` соответствует вашим требованиям