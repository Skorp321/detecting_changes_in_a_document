import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.models.regulation import Regulation

logger = logging.getLogger(__name__)


class RegulatoryMatcher:
    """Service for matching changes with relevant regulations"""
    
    def __init__(self):
        pass
    
    async def find_relevant_regulations(self, change_text: str, db: AsyncSession) -> List[Dict]:
        """Find regulations relevant to a specific change"""
        try:
            # Simple keyword-based matching for now
            query = select(Regulation).where(
                Regulation.active == True
            ).limit(5)
            
            result = await db.execute(query)
            regulations = result.scalars().all()
            
            # Convert to dictionaries
            relevant_regs = []
            for reg in regulations:
                relevant_regs.append({
                    'id': str(reg.id),
                    'title': reg.title,
                    'content': reg.content[:200] + '...',  # Truncate for response
                    'category': reg.category,
                    'services': reg.get_services()
                })
            
            return relevant_regs
            
        except Exception as e:
            logger.error(f"Error finding relevant regulations: {e}")
            return []
    
    async def get_regulations(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get paginated list of regulations"""
        try:
            query = select(Regulation).where(
                Regulation.active == True
            ).offset(skip).limit(limit)
            
            result = await db.execute(query)
            regulations = result.scalars().all()
            
            return [reg.to_dict() for reg in regulations]
            
        except Exception as e:
            logger.error(f"Error getting regulations: {e}")
            return [] 