from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class Regulation(BaseModel):
    """Regulation model for storing regulatory documents"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., max_length=500)
    content: str
    category: str = Field(..., max_length=100)
    
    # Metadata
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    # Status fields
    active: bool = True
    version: int = 1
    
    # Additional metadata
    author: Optional[str] = Field(None, max_length=100)
    source: Optional[str] = Field(None, max_length=200)
    effective_date: Optional[datetime] = None
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'active': self.active,
            'version': self.version,
            'author': self.author,
            'source': self.source,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
        }
    
    def get_services(self):
        """Get related services for this regulation"""
        # This would return associated services based on content analysis
        # For now, return default services based on category
        service_mapping = {
            'legal': ['Юридическая служба'],
            'compliance': ['Служба комплаенс'],
            'technical': ['Техническая служба'],
            'financial': ['Финансовая служба'],
            'security': ['Служба безопасности'],
            'safety': ['Служба безопасности'],
            'environmental': ['Служба экологии'],
        }
        return service_mapping.get(self.category.lower(), ['Юридическая служба'])
    
    def calculate_relevance(self, query_text: str) -> float:
        """Calculate relevance score for a given query"""
        # Simple relevance calculation based on keyword matching
        # In production, this would use more sophisticated NLP techniques
        query_words = set(query_text.lower().split())
        content_words = set(self.content.lower().split())
        title_words = set(self.title.lower().split())
        
        # Calculate overlap
        content_overlap = len(query_words.intersection(content_words))
        title_overlap = len(query_words.intersection(title_words))
        
        # Weight title matches higher
        relevance = (content_overlap + title_overlap * 2) / len(query_words)
        return min(relevance, 1.0)
    
    def get_excerpt(self, query_text: str, max_length: int = 200) -> str:
        """Get relevant excerpt from content"""
        # Simple excerpt extraction
        # In production, this would use more sophisticated text processing
        query_words = query_text.lower().split()
        content_lower = self.content.lower()
        
        # Find first occurrence of any query word
        best_pos = len(self.content)
        for word in query_words:
            pos = content_lower.find(word)
            if pos != -1 and pos < best_pos:
                best_pos = pos
        
        if best_pos == len(self.content):
            # No matches found, return beginning
            return self.content[:max_length] + ('...' if len(self.content) > max_length else '')
        
        # Extract excerpt around the match
        start = max(0, best_pos - max_length // 2)
        end = min(len(self.content), start + max_length)
        
        excerpt = self.content[start:end]
        if start > 0:
            excerpt = '...' + excerpt
        if end < len(self.content):
            excerpt = excerpt + '...'
        
        return excerpt
    
    def __repr__(self):
        return f"<Regulation(id='{self.id}', title='{self.title[:50]}...')>" 