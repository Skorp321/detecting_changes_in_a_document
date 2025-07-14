// Заглушка для web-vitals, пока не установлена зависимость
const getCLS = (callback: (metric: any) => void) => {}
const getFID = (callback: (metric: any) => void) => {}
const getFCP = (callback: (metric: any) => void) => {}
const getLCP = (callback: (metric: any) => void) => {}
const getTTFB = (callback: (metric: any) => void) => {}

interface WebVitalMetric {
  name: string
  value: number
  rating: 'good' | 'needs-improvement' | 'poor'
  delta: number
}

// Функция для отправки метрик на backend
const sendMetric = async (metric: WebVitalMetric) => {
  // Отправляем метрики только в production
  if (import.meta.env?.MODE !== 'production') {
    console.log('Web Vitals metric:', metric)
    return
  }

  try {
    const response = await fetch('/api/metrics', {
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
    console.error('Failed to send Web Vitals metric:', error)
    
    // Retry логика - попытка отправки через 5 секунд
    setTimeout(() => {
      sendMetric(metric).catch(() => {
        // Игнорируем ошибки при повторной попытке
      })
    }, 5000)
  }
}

// Функция для получения rating метрики
const getMetricRating = (name: string, value: number): 'good' | 'needs-improvement' | 'poor' => {
  const thresholds = {
    CLS: [0.1, 0.25],
    FID: [100, 300],
    FCP: [1800, 3000],
    LCP: [2500, 4000],
    TTFB: [800, 1800],
  }

  const limits = thresholds[name as keyof typeof thresholds] || [0, 0]
  const [good, poor] = limits
  
  if (value <= good) return 'good'
  if (value <= poor) return 'needs-improvement'
  return 'poor'
}

// Функция для обработки метрики
const handleMetric = (metric: any) => {
  const webVitalMetric: WebVitalMetric = {
    name: metric.name,
    value: metric.value,
    rating: getMetricRating(metric.name, metric.value),
    delta: metric.delta,
  }

  sendMetric(webVitalMetric)
}

// Функция для инициализации мониторинга Web Vitals
export const initWebVitals = () => {
  try {
    getCLS(handleMetric)
    getFID(handleMetric)
    getFCP(handleMetric)
    getLCP(handleMetric)
    getTTFB(handleMetric)
  } catch (error) {
    console.error('Failed to initialize Web Vitals:', error)
  }
}

// Функция для отправки кастомных метрик
export const reportCustomMetric = (name: string, value: number) => {
  const metric: WebVitalMetric = {
    name,
    value,
    rating: 'good', // Для кастомных метрик используем 'good' по умолчанию
    delta: value,
  }

  sendMetric(metric)
} 