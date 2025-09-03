import logging
import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import faiss
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(
    openai_api_key=settings.OPENAI_API_KEY,
    openai_api_base=settings.OPENAI_BASE_URL
)

# FAISS index path
FAISS_INDEX_PATH = Path(settings.FAISS_INDEX_PATH)
REGULATIONS_INDEX_PATH = FAISS_INDEX_PATH / "regulations"
SERVICES_INDEX_PATH = FAISS_INDEX_PATH / "services"
ANALYSIS_INDEX_PATH = FAISS_INDEX_PATH / "analysis"

# Ensure directories exist
for path in [REGULATIONS_INDEX_PATH, SERVICES_INDEX_PATH, ANALYSIS_INDEX_PATH]:
    path.mkdir(parents=True, exist_ok=True)

class FAISSDatabase:
    """FAISS-based database for storing and retrieving documents"""
    
    def __init__(self):
        self.regulations_store: Optional[FAISS] = None
        self.services_store: Optional[FAISS] = None
        self.analysis_store: Optional[FAISS] = None
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
            
            # Load services store
            if (SERVICES_INDEX_PATH / "index.faiss").exists():
                self.services_store = FAISS.load_local(
                    str(SERVICES_INDEX_PATH), 
                    embeddings,
                    allow_dangerous_deserialization=True
                )
            else:
                self.services_store = FAISS.from_texts(
                    ["Initial service"], 
                    embeddings
                )
                self.services_store.save_local(str(SERVICES_INDEX_PATH))
            
            # Load analysis store
            if (ANALYSIS_INDEX_PATH / "index.faiss").exists():
                self.analysis_store = FAISS.load_local(
                    str(ANALYSIS_INDEX_PATH), 
                    embeddings,
                    allow_dangerous_deserialization=True
                )
            else:
                self.analysis_store = FAISS.from_texts(
                    ["Initial analysis"], 
                    embeddings
                )
                self.analysis_store.save_local(str(ANALYSIS_INDEX_PATH))
                
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
            self.services_store = FAISS.from_texts(
                ["Initial service"], 
                embeddings
            )
            self.analysis_store = FAISS.from_texts(
                ["Initial analysis"], 
                embeddings
            )
            
            self.regulations_store.save_local(str(REGULATIONS_INDEX_PATH))
            self.services_store.save_local(str(SERVICES_INDEX_PATH))
            self.analysis_store.save_local(str(ANALYSIS_INDEX_PATH))
            
        except Exception as e:
            logger.error(f"Error creating empty FAISS stores: {e}")
    
    def _save_store(self, store: FAISS, path: Path):
        """Save FAISS store to disk"""
        try:
            store.save_local(str(path))
        except Exception as e:
            logger.error(f"Error saving FAISS store to {path}: {e}")

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
        # Create sample data if stores are empty
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
        
        # Sample services
        sample_services = [
            {
                'id': 'svc_001',
                'name': 'Служба безопасности',
                'description': 'Обеспечение безопасности персонала и имущества',
                'contact_info': 'security@company.com',
                'approval_type': 'required'
            },
            {
                'id': 'svc_002',
                'name': 'Финансовая служба',
                'description': 'Управление финансами и отчетностью',
                'contact_info': 'finance@company.com',
                'approval_type': 'required'
            },
            {
                'id': 'svc_003',
                'name': 'Юридическая служба',
                'description': 'Правовое сопровождение деятельности',
                'contact_info': 'legal@company.com',
                'approval_type': 'required'
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
        
        # Add services to FAISS
        service_docs = []
        for svc in sample_services:
            doc = Document(
                page_content=f"{svc['name']} {svc['description']}",
                metadata=svc
            )
            service_docs.append(doc)
        
        if service_docs:
            faiss_db.services_store = FAISS.from_documents(
                service_docs, 
                embeddings
            )
            faiss_db._save_store(faiss_db.services_store, SERVICES_INDEX_PATH)
            
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")

# Database cleanup
async def close_db():
    """Close FAISS database connections"""
    try:
        # Save all stores before closing
        if faiss_db.regulations_store:
            faiss_db._save_store(faiss_db.regulations_store, REGULATIONS_INDEX_PATH)
        if faiss_db.services_store:
            faiss_db._save_store(faiss_db.services_store, SERVICES_INDEX_PATH)
        if faiss_db.analysis_store:
            faiss_db._save_store(faiss_db.analysis_store, ANALYSIS_INDEX_PATH)
        logger.info("FAISS database connections closed")
    except Exception as e:
        logger.error(f"Error closing FAISS database: {e}")

# Health check function
async def check_db_health() -> bool:
    """Check FAISS database health"""
    try:
        return (
            faiss_db.regulations_store is not None and
            faiss_db.services_store is not None and
            faiss_db.analysis_store is not None
        )
    except Exception as e:
        logger.error(f"FAISS database health check failed: {e}")
        return False 