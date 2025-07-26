// Заглушка для web-vitals, пока не установлена зависимость
const getCLS = (_callback: (metric: any) => void) => {}
const getFID = (_callback: (metric: any) => void) => {}
const getFCP = (_callback: (metric: any) => void) => {}
const getLCP = (_callback: (metric: any) => void) => {}
const getTTFB = (_callback: (metric: any) => void) => {}

interface WebVitalMetric {
  name: string
  value: number
  rating: 'good' | 'needs-improvement' | 'poor'
  delta: number
}

// Функция для отправки метрик на backend
const sendMetric = async (metric: WebVitalMetric) => {
  // Отправляем метрики только в production
  console.log('Web Vitals metric:', metric)

  try {
    const response = await fetch('/api/metrics/web-vitals', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(metric),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
  } catch (error) {
    console.error('Failed to send metric:', error)
  }
}

// Функция для получения рейтинга метрики
const getMetricRating = (name: string, value: number): 'good' | 'needs-improvement' | 'poor' => {
  const thresholds = {
    CLS: { good: 0.1, poor: 0.25 },
    FID: { good: 100, poor: 300 },
    FCP: { good: 1800, poor: 3000 },
    LCP: { good: 2500, poor: 4000 },
    TTFB: { good: 800, poor: 1800 }
  }
  
  const threshold = thresholds[name as keyof typeof thresholds]
  if (!threshold) return 'good'
  
  const good = threshold.good || 0
  const poor = threshold.poor || 0
  
  if (value <= good) return 'good'
  if (value <= poor) return 'needs-improvement'
  return 'poor'
}

// Основная функция для инициализации Web Vitals
export const initWebVitals = () => {
  const handleMetric = (metric: any) => {
    const webVitalMetric: WebVitalMetric = {
      name: metric.name,
      value: metric.value,
      rating: getMetricRating(metric.name, metric.value),
      delta: metric.delta
    }
    
    sendMetric(webVitalMetric)
  }

  // Инициализируем метрики
  getCLS(handleMetric)
  getFID(handleMetric)
  getFCP(handleMetric)
  getLCP(handleMetric)
  getTTFB(handleMetric)
}

// Функция для отправки пользовательских метрик
export const sendCustomMetric = (name: string, value: number) => {
  const metric: WebVitalMetric = {
    name: `custom_${name}`,
    value,
    rating: 'good',
    delta: 0
  }
  
  sendMetric(metric)
}

// Функция для измерения времени загрузки компонентов
export const measureComponentLoad = (componentName: string, startTime: number) => {
  const loadTime = performance.now() - startTime
  sendCustomMetric(`component_load_${componentName}`, loadTime)
}

// Функция для измерения времени API запросов
export const measureApiCall = (endpoint: string, startTime: number) => {
  const duration = performance.now() - startTime
  sendCustomMetric(`api_call_${endpoint.replace(/[^a-zA-Z0-9]/g, '_')}`, duration)
}

export default initWebVitals 