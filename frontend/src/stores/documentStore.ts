import { create } from 'zustand';
import { AnalysisResult } from '../types';

interface DocumentState {
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

interface DocumentActions {
  setReferenceDoc: (file: File | null) => void;
  setClientDoc: (file: File | null) => void;
  setAnalysisResults: (results: AnalysisResult[] | null) => void;
  setIsAnalyzing: (analyzing: boolean) => void;
  setUploadProgress: (type: 'reference' | 'client', progress: number) => void;
  setError: (error: string | null) => void;
  clearAll: () => void;
}

type DocumentStore = DocumentState & DocumentActions;

const initialState: DocumentState = {
  referenceDoc: null,
  clientDoc: null,
  analysisResults: null,
  isAnalyzing: false,
  uploadProgress: {
    reference: 0,
    client: 0,
  },
  error: null,
};

export const useDocumentStore = create<DocumentStore>((set) => ({
  ...initialState,
  
  setReferenceDoc: (file) => {
    set({ referenceDoc: file });
    if (file) {
      set({ error: null });
    }
  },
  
  setClientDoc: (file) => {
    set({ clientDoc: file });
    if (file) {
      set({ error: null });
    }
  },
  
  setAnalysisResults: (results) => {
    set({ analysisResults: results });
  },
  
  setIsAnalyzing: (analyzing) => {
    set({ isAnalyzing: analyzing });
    if (analyzing) {
      set({ error: null });
    }
  },
  
  setUploadProgress: (type, progress) => {
    set((state) => ({
      uploadProgress: {
        ...state.uploadProgress,
        [type]: progress,
      },
    }));
  },
  
  setError: (error) => {
    set({ error });
    if (error) {
      set({ isAnalyzing: false });
    }
  },
  
  clearAll: () => {
    set(initialState);
  },
})); 