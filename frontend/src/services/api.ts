import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { saveAs } from 'file-saver';
import { 
  CompareDocumentsRequest, 
  CompareDocumentsResponse, 
  AnalysisResult, 
  ExportFormat 
} from '../types';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  timeout: 300000, // 5 minutes for long document processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API functions
export const analyzeDocuments = async (
  request: CompareDocumentsRequest
): Promise<CompareDocumentsResponse> => {
  try {
    const formData = new FormData();
    formData.append('reference_doc', request.referenceDoc);
    formData.append('client_doc', request.clientDoc);

    const response = await api.post('/compare', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / (progressEvent.total || 1)
        );
        console.log(`Upload progress: ${percentCompleted}%`);
      },
    });

    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('Document analysis error:', error);
    
    if (axios.isAxiosError(error)) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          'Ошибка при анализе документов';
      
      return {
        success: false,
        error: errorMessage,
      };
    }
    
    return {
      success: false,
      error: 'Неизвестная ошибка при анализе документов',
    };
  }
};

export const exportResults = async (
  results: AnalysisResult[],
  format: ExportFormat
): Promise<void> => {
  try {
    const response = await api.post('/export', {
      results,
      format,
    }, {
      responseType: 'blob',
    });

    const blob = new Blob([response.data], {
      type: response.headers['content-type'],
    });

    const filename = `analysis_results_${new Date().toISOString().split('T')[0]}.${format}`;
    saveAs(blob, filename);
  } catch (error) {
    console.error('Export error:', error);
    throw new Error('Ошибка при экспорте результатов');
  }
};

export const getRegulations = async (): Promise<any[]> => {
  try {
    const response = await api.get('/regulations');
    return response.data;
  } catch (error) {
    console.error('Error fetching regulations:', error);
    throw new Error('Ошибка при получении нормативных документов');
  }
};

export const getServices = async (): Promise<any[]> => {
  try {
    const response = await api.get('/services');
    return response.data;
  } catch (error) {
    console.error('Error fetching services:', error);
    throw new Error('Ошибка при получении списка служб');
  }
};

export const healthCheck = async (): Promise<{ status: string }> => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check error:', error);
    throw new Error('Сервис недоступен');
  }
};

// Utility functions
export const validateFileType = (file: File): boolean => {
  const allowedTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
  ];
  return allowedTypes.includes(file.type);
};

export const validateFileSize = (file: File, maxSizeMB: number = 10): boolean => {
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  return file.size <= maxSizeBytes;
};

export const getFileExtension = (filename: string): string => {
  return filename.split('.').pop()?.toLowerCase() || '';
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Error handling utilities
export const handleApiError = (error: any): string => {
  if (axios.isAxiosError(error)) {
    if (error.response?.status === 413) {
      return 'Файл слишком большой для обработки';
    }
    if (error.response?.status === 415) {
      return 'Неподдерживаемый формат файла';
    }
    if (error.response?.status === 422) {
      return 'Некорректные данные в запросе';
    }
    if (error.response?.status === 500) {
      return 'Внутренняя ошибка сервера';
    }
    if (error.response?.status === 503) {
      return 'Сервис временно недоступен';
    }
    
    return error.response?.data?.message || error.message || 'Ошибка сети';
  }
  
  return 'Неизвестная ошибка';
};

export default api; 