import logging
import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader
)
import glob
import shutil

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize multilingual-e5-large embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-large",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# FAISS index path
FAISS_INDEX_PATH = Path(settings.FAISS_INDEX_PATH)
REGULATIONS_INDEX_PATH = FAISS_INDEX_PATH / "regulations"

# Ensure directories exist
REGULATIONS_INDEX_PATH.mkdir(parents=True, exist_ok=True)

class FAISSDatabase:
    """FAISS-based database for storing and retrieving documents"""
    
    def __init__(self):
        self.regulations_store: Optional[FAISS] = None
        self._load_stores()
    
    def _load_stores(self):
        """Load existing FAISS stores or create new ones"""
        try:
            # Load regulations store
            if (REGULATIONS_INDEX_PATH / "index.faiss").exists():
                self.regulations_store = FAISS.load_local(
                    str(REGULATIONS_INDEX_PATH), 
                    embeddings,
                    allow_dangerous_deserialization=True
                )
            else:
                self.regulations_store = FAISS.from_texts(
                    ["Initial regulation"], 
                    embeddings
                )
                self.regulations_store.save_local(str(REGULATIONS_INDEX_PATH))
                
        except Exception as e:
            logger.error(f"Error loading FAISS stores: {e}")
            # Create empty stores if loading fails
            self._create_empty_stores()
    
    def _create_empty_stores(self):
        """Create empty FAISS stores"""
        try:
            self.regulations_store = FAISS.from_texts(
                ["Initial regulation"], 
                embeddings
            )
            
            self.regulations_store.save_local(str(REGULATIONS_INDEX_PATH))
            
        except Exception as e:
            logger.error(f"Error creating empty FAISS stores: {e}")
    
    def _save_store(self, store: FAISS, path: Path):
        """Save FAISS store to disk"""
        try:
            store.save_local(str(path))
        except Exception as e:
            logger.error(f"Error saving FAISS store to {path}: {e}")
    
    def _load_documents_from_directory(self, directory_path: str) -> List[Document]:
        """Load documents from directory containing .docx, .txt, .pdf files"""
        documents = []
        directory = Path(directory_path)
        
        if not directory.exists():
            logger.warning(f"Directory {directory_path} does not exist")
            return documents
        
        # Supported file extensions
        file_patterns = ["*.txt", "*.pdf", "*.docx"]
        
        for pattern in file_patterns:
            for file_path in directory.glob(pattern):
                try:
                    logger.info(f"Loading document: {file_path}")
                    
                    if file_path.suffix.lower() == '.txt':
                        loader = TextLoader(str(file_path), encoding='utf-8')
                    elif file_path.suffix.lower() == '.pdf':
                        loader = PyPDFLoader(str(file_path))
                    elif file_path.suffix.lower() == '.docx':
                        loader = Docx2txtLoader(str(file_path))
                    else:
                        continue
                    
                    docs = loader.load()
                    
                    # Add file metadata
                    for doc in docs:
                        doc.metadata.update({
                            'source_file': str(file_path),
                            'file_name': file_path.name,
                            'file_type': file_path.suffix.lower()
                        })
                    
                    documents.extend(docs)
                    
                except Exception as e:
                    logger.error(f"Error loading document {file_path}: {e}")
        
        logger.info(f"Loaded {len(documents)} documents from {directory_path}")
        return documents
    
    def _split_documents(self, documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
        """Split documents into chunks using RecursiveCharacterTextSplitter"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        split_docs = text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(split_docs)} chunks")
        return split_docs
    
    def build_database_from_files(self, documents_directory: str, 
                                 chunk_size: int = 1000, chunk_overlap: int = 200, force_rebuild: bool = False):
        """
        Build database from files in directory
        
        Args:
            documents_directory: Path to directory containing documents
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            force_rebuild: Force rebuild even if database exists
        """
        try:
            store_path = REGULATIONS_INDEX_PATH
            
            # Check if database exists and force_rebuild is False
            if not force_rebuild and (store_path / "index.faiss").exists():
                logger.info("Database already exists, loading from disk")
                self._load_stores()
                return
            
            # Load documents from directory
            documents = self._load_documents_from_directory(documents_directory)
            
            if not documents:
                logger.warning(f"No documents found in {documents_directory}")
                return
            
            # Split documents into chunks
            split_docs = self._split_documents(documents, chunk_size, chunk_overlap)
            
            if not split_docs:
                logger.warning("No document chunks created")
                return
            
            # Create FAISS store from documents
            logger.info(f"Creating FAISS store with {len(split_docs)} chunks")
            store = FAISS.from_documents(split_docs, embeddings)
            
            # Save store
            if force_rebuild and store_path.exists():
                shutil.rmtree(store_path)
                store_path.mkdir(parents=True, exist_ok=True)
            
            store.save_local(str(store_path))
            
            # Update instance variable
            self.regulations_store = store
            
            logger.info(f"Successfully built database from {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error building database from files: {e}")
            raise
    
    def rebuild_database_from_files(self, documents_directory: str,
                                   chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Force rebuild database from files
        
        Args:
            documents_directory: Path to directory containing documents
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        logger.info(f"Force rebuilding database from {documents_directory}")
        self.build_database_from_files(
            documents_directory=documents_directory,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            force_rebuild=True
        )
    
    def load_or_build_database(self, documents_directory: str,
                              chunk_size: int = 1000, chunk_overlap: int = 200, force_rebuild: bool = False):
        """
        Load existing database or build from files if not exists
        
        Args:
            documents_directory: Path to directory containing documents
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            force_rebuild: Force rebuild even if database exists
        """
        self.build_database_from_files(
            documents_directory=documents_directory,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            force_rebuild=force_rebuild
        )

# Global FAISS database instance
faiss_db = FAISSDatabase()

# Dependency to get FAISS database
def get_faiss_db() -> FAISSDatabase:
    """Get FAISS database instance"""
    return faiss_db

# Database initialization
async def init_db():
    """Initialize FAISS database"""
    try:
        # Очищаем существующий FAISS индекс если требуется принудительное пересоздание
        if settings.FORCE_REBUILD_FAISS:
            logger.info("Принудительное пересоздание FAISS индекса...")
            if REGULATIONS_INDEX_PATH.exists():
                shutil.rmtree(REGULATIONS_INDEX_PATH)
                logger.info(f"Удален существующий FAISS индекс: {REGULATIONS_INDEX_PATH}")
            REGULATIONS_INDEX_PATH.mkdir(parents=True, exist_ok=True)
        
        # Try to build database from documents directory
        documents_path = settings.DOCUMENTS_PATH
        
        if Path(documents_path).exists():
            logger.info(f"Building database from documents in {documents_path}")
            
            # Используем force_rebuild=True если требуется принудительное пересоздание
            force_rebuild = settings.FORCE_REBUILD_FAISS
            faiss_db.load_or_build_database(
                documents_directory=documents_path,
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=200,
                force_rebuild=force_rebuild
            )
        else:
            logger.warning(f"Documents directory {documents_path} not found, creating sample data")
            # Create sample data if no documents directory exists
            if not faiss_db.regulations_store or faiss_db.regulations_store.index.ntotal == 1:
                await _create_sample_data()
        
        logger.info("FAISS database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing FAISS database: {e}")
        raise

async def _create_sample_data():
    """Create sample data for the FAISS stores"""
    try:
        # Sample regulations
        sample_regulations = [
            {
                'id': 'reg_001',
                'title': 'Правила безопасности труда',
                'content': 'Основные правила безопасности труда на производстве. Требования к оборудованию, защитным средствам и процедурам.',
                'category': 'safety',
                'active': True
            },
            {
                'id': 'reg_002',
                'title': 'Положение о финансовой отчетности',
                'content': 'Требования к составлению и представлению финансовой отчетности. Сроки подачи и форматы документов.',
                'category': 'financial',
                'active': True
            },
            {
                'id': 'reg_003',
                'title': 'Инструкция по охране окружающей среды',
                'content': 'Мероприятия по охране окружающей среды. Контроль выбросов и утилизация отходов.',
                'category': 'environmental',
                'active': True
            }
        ]
        
        # Add regulations to FAISS
        regulation_docs = []
        for reg in sample_regulations:
            doc = Document(
                page_content=f"{reg['title']} {reg['content']}",
                metadata=reg
            )
            regulation_docs.append(doc)
        
        if regulation_docs:
            faiss_db.regulations_store = FAISS.from_documents(
                regulation_docs, 
                embeddings
            )
            faiss_db._save_store(faiss_db.regulations_store, REGULATIONS_INDEX_PATH)
            
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")

# Database cleanup
async def close_db():
    """Close FAISS database connections"""
    try:
        # Save store before closing
        if faiss_db.regulations_store:
            faiss_db._save_store(faiss_db.regulations_store, REGULATIONS_INDEX_PATH)
        logger.info("FAISS database connections closed")
    except Exception as e:
        logger.error(f"Error closing FAISS database: {e}")

# Health check function
async def check_db_health() -> bool:
    """Check FAISS database health"""
    try:
        return faiss_db.regulations_store is not None
    except Exception as e:
        logger.error(f"FAISS database health check failed: {e}")
        return False

# Document processing functions
def build_database_from_documents(documents_directory: str,
                                 chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Build database from documents directory
    
    Args:
        documents_directory: Path to directory containing .docx, .txt, .pdf files
        chunk_size: Size of text chunks for splitting
        chunk_overlap: Overlap between chunks
    """
    faiss_db.load_or_build_database(
        documents_directory=documents_directory,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

def rebuild_database_from_documents(documents_directory: str,
                                   chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Force rebuild database from documents directory
    
    Args:
        documents_directory: Path to directory containing .docx, .txt, .pdf files
        chunk_size: Size of text chunks for splitting
        chunk_overlap: Overlap between chunks
    """
    faiss_db.rebuild_database_from_files(
        documents_directory=documents_directory,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    ) 