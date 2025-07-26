# Мониторинг Oozo

Этот документ описывает настройку и использование системы мониторинга для проекта Oozo с использованием Prometheus и Grafana.

## Компоненты системы мониторинга

### 1. Prometheus
- **Порт**: 9090
- **Описание**: Сбор и хранение метрик
- **Конфигурация**: `prometheus.yml`
- **Правила алертов**: `alert_rules.yml`

### 2. Grafana
- **Порт**: 3001
- **Описание**: Визуализация метрик и дашборды
- **Логин**: admin
- **Пароль**: admin

### 3. AlertManager
- **Порт**: 9093
- **Описание**: Управление алертами и уведомлениями
- **Конфигурация**: `alertmanager.yml`

### 4. Node Exporter
- **Порт**: 9100
- **Описание**: Сбор системных метрик (CPU, память, диск)

## Запуск мониторинга

### Базовый запуск
```bash
# Из корня проекта
docker-compose -f monitoring/docker-compose.monitoring.yml up -d
```

### Запуск с основными сервисами
```bash
# Запуск основных сервисов
docker-compose up -d

# Запуск мониторинга
docker-compose -f monitoring/docker-compose.monitoring.yml up -d
```

### Проверка состояния
```bash
# Проверка контейнеров
docker-compose -f monitoring/docker-compose.monitoring.yml ps

# Просмотр логов
docker-compose -f monitoring/docker-compose.monitoring.yml logs -f
```

## Доступ к интерфейсам

### Prometheus
- URL: http://localhost:9090
- Функции: Просмотр метрик, выполнение запросов PromQL, проверка состояния алертов

### Grafana
- URL: http://localhost:3001
- Логин: admin / admin
- Дашборды:
  - **Oozo System Overview**: Общий обзор системы
  - **Infrastructure Monitoring**: Мониторинг инфраструктуры

### AlertManager
- URL: http://localhost:9093
- Функции: Управление алертами, настройка уведомлений

## Метрики

### Системные метрики
- `http_requests_total` - Общее количество HTTP запросов
- `http_request_duration_seconds` - Время выполнения HTTP запросов
- `document_processing_total` - Количество обработанных документов
- `document_processing_duration_seconds` - Время обработки документов
- `llm_analysis_total` - Количество LLM анализов
- `llm_analysis_duration_seconds` - Время LLM анализа

### Web Vitals метрики
- `web_vitals_lcp` - Largest Contentful Paint
- `web_vitals_fid` - First Input Delay
- `web_vitals_cls` - Cumulative Layout Shift
- `web_vitals_fcp` - First Contentful Paint
- `web_vitals_ttfb` - Time to First Byte

### Инфраструктурные метрики
- `node_cpu_seconds_total` - Использование CPU
- `node_memory_*` - Использование памяти
- `node_filesystem_*` - Использование дискового пространства
- `node_load*` - Загрузка системы

## Алерты

### Критические алерты
- **ServiceDown**: Сервис недоступен более 2 минут
- **HighMemoryUsage**: Использование памяти > 90%

### Предупреждения
- **HighResponseTime**: Время отклика > 5 секунд
- **HighCPUUsage**: Использование CPU > 80%
- **HighDiskUsage**: Использование диска > 85%
- **WebVitalsHighLCP**: LCP > 4 секунд
- **WebVitalsHighCLS**: CLS > 0.25
- **WebVitalsHighFID**: FID > 300ms

## Настройка алертов

### Email уведомления
Отредактируйте `alertmanager.yml`:
```yaml
global:
  smtp_smarthost: 'your-smtp-server:587'
  smtp_from: 'alerts@yourdomain.com'
  smtp_auth_username: 'your-email@yourdomain.com'
  smtp_auth_password: 'your-password'

receivers:
  - name: 'email'
    email_configs:
      - to: 'admin@yourdomain.com'
        subject: 'Oozo Alert: {{ .GroupLabels.alertname }}'
```

### Webhook уведомления
Для интеграции с Slack, Discord или другими системами:
```yaml
receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        send_resolved: true
```

## Дашборды

### Импорт дашбордов
Дашборды автоматически загружаются из папки `grafana/dashboards/`:
- `oozo-overview.json` - Обзор системы Oozo
- `infrastructure.json` - Мониторинг инфраструктуры

### Создание собственных дашбордов
1. Создайте дашборд в Grafana UI
2. Экспортируйте JSON
3. Сохраните в `grafana/dashboards/`
4. Перезапустите Grafana

## Обслуживание

### Очистка старых данных
Prometheus автоматически удаляет данные старше 200 часов.

### Резервное копирование
```bash
# Создание бэкапа данных Prometheus
docker run --rm -v oozo_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz /data

# Создание бэкапа данных Grafana
docker run --rm -v oozo_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz /data
```

### Восстановление
```bash
# Восстановление данных Prometheus
docker run --rm -v oozo_prometheus_data:/data -v $(pwd):/backup alpine tar xzf /backup/prometheus-backup.tar.gz -C /

# Восстановление данных Grafana
docker run --rm -v oozo_grafana_data:/data -v $(pwd):/backup alpine tar xzf /backup/grafana-backup.tar.gz -C /
```

## Troubleshooting

### Проблемы с подключением
1. Убедитесь, что все контейнеры запущены
2. Проверьте сетевые подключения
3. Проверьте логи контейнеров

### Отсутствие метрик
1. Проверьте эндпоинт `/api/metrics` в backend
2. Убедитесь, что Prometheus может достучаться до сервисов
3. Проверьте конфигурацию `prometheus.yml`

### Алерты не работают
1. Проверьте состояние AlertManager
2. Убедитесь в правильности конфигурации `alertmanager.yml`
3. Проверьте правила алертов в `alert_rules.yml`

## Полезные команды

```bash
# Перезапуск мониторинга
docker-compose -f monitoring/docker-compose.monitoring.yml restart

# Остановка мониторинга
docker-compose -f monitoring/docker-compose.monitoring.yml down

# Просмотр использования ресурсов
docker-compose -f monitoring/docker-compose.monitoring.yml top

# Обновление конфигурации без перезапуска
docker-compose -f monitoring/docker-compose.monitoring.yml kill -s HUP prometheus
``` 