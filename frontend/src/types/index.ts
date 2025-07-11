// Document upload types
export interface DocumentUploadStatus {
  uploading: boolean;
  progress: number;
  error: string | null;
  success: boolean;
}

export interface DocumentFile {
  file: File;
  preview?: string;
  type: 'reference' | 'client';
  uploadStatus: DocumentUploadStatus;
}

// Analysis result types
export interface AnalysisResult {
  id: string;
  originalText: string;
  modifiedText: string;
  llmComment: string;
  requiredServices: string[];
  changeType: 'addition' | 'deletion' | 'modification';
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  createdAt: string;
  highlightedOriginal?: string;
  highlightedModified?: string;
}

export interface AnalysisResponse {
  analysisId: string;
  changes: AnalysisResult[];
  summary: {
    totalChanges: number;
    criticalChanges: number;
    processingTime: string;
    documentPair: {
      referenceDoc: string;
      clientDoc: string;
    };
  };
}

// API request/response types
export interface CompareDocumentsRequest {
  referenceDoc: File;
  clientDoc: File;
}

export interface CompareDocumentsResponse {
  success: boolean;
  data?: AnalysisResponse;
  error?: string;
}

// File validation types
export interface FileValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface FileConstraints {
  maxSize: number;
  allowedExtensions: string[];
  maxPages?: number;
}

// Component prop types
export interface DocumentUploadProps {
  onFilesChange?: (files: { reference: File | null; client: File | null }) => void;
  disabled?: boolean;
  className?: string;
}

export interface AnalysisButtonProps {
  disabled?: boolean;
  onAnalyze?: () => void;
  className?: string;
}

export interface ResultsTableProps {
  results?: AnalysisResult[];
  loading?: boolean;
  onExport?: (format: 'csv' | 'pdf' | 'word') => void;
  className?: string;
}

// State management types
export interface DocumentState {
  referenceDoc: File | null;
  clientDoc: File | null;
  analysisResults: AnalysisResult[] | null;
  isAnalyzing: boolean;
  uploadProgress: {
    reference: number;
    client: number;
  };
  error: string | null;
}

// Error types
export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}

// Export types
export type ExportFormat = 'csv' | 'pdf' | 'word';

export interface ExportOptions {
  format: ExportFormat;
  includeMetadata: boolean;
  filename?: string;
}

// Regulation types
export interface Regulation {
  id: string;
  title: string;
  content: string;
  category: string;
  services: string[];
  createdAt: string;
  updatedAt: string;
}

// Service types
export interface Service {
  id: string;
  name: string;
  description: string;
  contactInfo: string;
  approvalType: 'required' | 'optional' | 'conditional';
  active: boolean;
}

// Analysis configuration
export interface AnalysisConfig {
  includeMinorChanges: boolean;
  confidenceThreshold: number;
  maxProcessingTime: number;
  language: 'ru' | 'en';
} 