import time
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from prometheus_client.core import REGISTRY
import logging

logger = logging.getLogger(__name__)

# Создаем основные метрики для мониторинга
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

document_processing_count = Counter(
    'document_processing_total',
    'Total document processing requests',
    ['type', 'status']
)

document_processing_duration = Histogram(
    'document_processing_duration_seconds',
    'Document processing duration in seconds',
    ['type']
)

llm_analysis_count = Counter(
    'llm_analysis_total',
    'Total LLM analysis requests',
    ['status']
)

llm_analysis_duration = Histogram(
    'llm_analysis_duration_seconds',
    'LLM analysis duration in seconds'
)

database_connection_pool = Gauge(
    'database_connection_pool_size',
    'Database connection pool size',
    ['state']
)

active_sessions = Gauge(
    'active_sessions_total',
    'Total active user sessions'
)

# Web Vitals метрики
web_vitals_lcp = Gauge(
    'web_vitals_lcp',
    'Largest Contentful Paint metric'
)

web_vitals_fid = Gauge(
    'web_vitals_fid',
    'First Input Delay metric'
)

web_vitals_cls = Gauge(
    'web_vitals_cls',
    'Cumulative Layout Shift metric'
)

web_vitals_fcp = Gauge(
    'web_vitals_fcp',
    'First Contentful Paint metric'
)

web_vitals_ttfb = Gauge(
    'web_vitals_ttfb',
    'Time to First Byte metric'
)

class MetricsService:
    """Сервис для управления метриками Prometheus"""
    
    def __init__(self):
        self.registry = REGISTRY
        
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Записать метрику HTTP запроса"""
        request_count.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        
    def record_document_processing(self, doc_type: str, status: str, duration: float):
        """Записать метрику обработки документа"""
        document_processing_count.labels(type=doc_type, status=status).inc()
        document_processing_duration.labels(type=doc_type).observe(duration)
        
    def record_llm_analysis(self, status: str, duration: float):
        """Записать метрику LLM анализа"""
        llm_analysis_count.labels(status=status).inc()
        llm_analysis_duration.observe(duration)
        
    def update_db_pool_size(self, active: int, idle: int):
        """Обновить метрики пула соединений БД"""
        database_connection_pool.labels(state='active').set(active)
        database_connection_pool.labels(state='idle').set(idle)
        
    def update_active_sessions(self, count: int):
        """Обновить количество активных сессий"""
        active_sessions.set(count)
        
    def record_web_vitals(self, metric_name: str, value: float):
        """Записать Web Vitals метрику"""
        metric_map = {
            'LCP': web_vitals_lcp,
            'FID': web_vitals_fid,
            'CLS': web_vitals_cls,
            'FCP': web_vitals_fcp,
            'TTFB': web_vitals_ttfb
        }
        
        if metric_name in metric_map:
            metric_map[metric_name].set(value)
            logger.info(f"Web Vitals metric recorded: {metric_name} = {value}")
        else:
            logger.warning(f"Unknown Web Vitals metric: {metric_name}")
    
    def get_metrics(self) -> str:
        """Получить все метрики в формате Prometheus"""
        return generate_latest(self.registry)
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Получить метрики здоровья системы"""
        return {
            "request_count": request_count._value._value,
            "document_processing_count": document_processing_count._value._value,
            "llm_analysis_count": llm_analysis_count._value._value,
            "active_sessions": active_sessions._value._value,
            "timestamp": time.time()
        }

# Глобальный экземпляр сервиса метрик
metrics_service = MetricsService() 