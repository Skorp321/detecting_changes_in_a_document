import React, { Suspense } from 'react'
import { Spin } from 'antd'

// Lazy imports компонентов
const DocumentUploadLazy = React.lazy(() => import('./DocumentUpload'))
const ResultsTableLazy = React.lazy(() => import('./ResultsTable'))
const AnalysisButtonLazy = React.lazy(() => import('./AnalysisButton'))

// Компонент загрузки
const LoadingSpinner = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    minHeight: '200px' 
  }}>
    <Spin size="large" />
  </div>
)

// Обертки с Suspense
export const DocumentUpload = (props: any) => (
  <Suspense fallback={<LoadingSpinner />}>
    <DocumentUploadLazy {...props} />
  </Suspense>
)

export const ResultsTable = (props: any) => (
  <Suspense fallback={<LoadingSpinner />}>
    <ResultsTableLazy {...props} />
  </Suspense>
)

export const AnalysisButton = (props: any) => (
  <Suspense fallback={<LoadingSpinner />}>
    <AnalysisButtonLazy {...props} />
  </Suspense>
) 