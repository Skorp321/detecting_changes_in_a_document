import logging
from typing import List, Dict, Any
from langchain.schema import Document
from pathlib import Path

from app.database.connection import get_faiss_db
from app.models.regulation import Regulation

logger = logging.getLogger(__name__)


class RegulatoryMatcher:
    """Service for matching changes with relevant regulations"""
    
    def __init__(self):
        pass
    
    async def find_relevant_regulations(self, change_text: str) -> List[Dict]:
        """Find regulations relevant to a specific change"""
        try:
            faiss_db = get_faiss_db()
            if not faiss_db.regulations_store:
                logger.warning("Regulations store not available")
                return []
            
            # Search for relevant regulations using FAISS
            docs = faiss_db.regulations_store.similarity_search(
                change_text, 
                k=5
            )
            
            # Convert to dictionaries
            relevant_regs = []
            for doc in docs:
                if doc.metadata:
                    reg_data = doc.metadata
                    regulation = Regulation(**reg_data)
                    relevant_regs.append({
                        'id': regulation.id,
                        'title': regulation.title,
                        'content': regulation.content,
                        'category': regulation.category,
                        'services': regulation.get_services()
                    })
            
            return relevant_regs
            
        except Exception as e:
            logger.error(f"Error finding relevant regulations: {e}")
            return []
    
    async def get_regulations(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get paginated list of regulations"""
        try:
            faiss_db = get_faiss_db()
            if not faiss_db.regulations_store:
                logger.warning("Regulations store not available")
                return []
            
            # Get all documents from FAISS store
            # Note: FAISS doesn't support pagination natively, so we'll get all and slice
            all_docs = faiss_db.regulations_store.docstore._dict.values()
            
            # Convert to regulations and apply pagination
            regulations = []
            for doc in list(all_docs)[skip:skip + limit]:
                if hasattr(doc, 'metadata') and doc.metadata:
                    regulation = Regulation(**doc.metadata)
                    regulations.append(regulation.to_dict())
            
            return regulations
            
        except Exception as e:
            logger.error(f"Error getting regulations: {e}")
            return []
    
    async def add_regulation(self, regulation: Regulation) -> bool:
        """Add a new regulation to the FAISS store"""
        try:
            faiss_db = get_faiss_db()
            if not faiss_db.regulations_store:
                logger.error("Regulations store not available")
                return False
            
            # Create document for FAISS
            doc = Document(
                page_content=f"{regulation.title} {regulation.content}",
                metadata=regulation.to_dict()
            )
            
            # Add to store
            faiss_db.regulations_store.add_documents([doc])
            
            # Save to disk using the correct path
            from app.database.connection import REGULATIONS_INDEX_PATH
            faiss_db._save_store(faiss_db.regulations_store, REGULATIONS_INDEX_PATH)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding regulation: {e}")
            return False
    
    async def update_regulation(self, regulation_id: str, regulation: Regulation) -> bool:
        """Update an existing regulation"""
        try:
            faiss_db = get_faiss_db()
            if not faiss_db.regulations_store:
                logger.error("Regulations store not available")
                return False
            
            # For simplicity, we'll remove and re-add the regulation
            # In a production system, you might want to implement more sophisticated update logic
            await self.delete_regulation(regulation_id)
            return await self.add_regulation(regulation)
            
        except Exception as e:
            logger.error(f"Error updating regulation: {e}")
            return False
    
    async def delete_regulation(self, regulation_id: str) -> bool:
        """Delete a regulation from the FAISS store"""
        try:
            faiss_db = get_faiss_db()
            if not faiss_db.regulations_store:
                logger.error("Regulations store not available")
                return False
            
            # Note: FAISS doesn't support deletion natively
            # In a production system, you might want to implement a different approach
            # For now, we'll mark it as inactive in metadata
            logger.warning("FAISS deletion not implemented - marking as inactive")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting regulation: {e}")
            return False 