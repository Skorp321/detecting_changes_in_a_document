#!/bin/bash

echo "🔧 Останавливаем контейнеры..."
docker-compose down

echo "🗑️  Удаляем старые образы..."
docker-compose rm -f

echo "🏗️  Пересобираем приложение..."
docker-compose build --no-cache

echo "🚀 Запускаем приложение..."
docker-compose up -d

echo "⏳ Ожидаем запуска сервисов..."
sleep 10

echo "✅ Проверяем статус..."
docker-compose ps

echo "🔍 Проверяем health endpoints..."
echo -n "Frontend health: "
curl -s http://localhost:3000/health || echo "❌ Failed"
echo -n "Backend health: "
curl -s http://localhost:3000/api/health | jq -r '.status' || echo "❌ Failed"

echo ""
echo "📝 Логи последних событий:"
docker-compose logs --tail=20

echo ""
echo "✨ Готово! Приложение доступно по адресу: http://localhost:3000"