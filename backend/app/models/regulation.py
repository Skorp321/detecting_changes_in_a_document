from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.connection import Base


class Regulation(Base):
    """Regulation model for storing regulatory documents"""
    
    __tablename__ = "regulations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    
    # Full-text search column
    search_vector = Column(TSVECTOR)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status fields
    active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    
    # Additional metadata
    author = Column(String(100), nullable=True)
    source = Column(String(200), nullable=True)
    effective_date = Column(DateTime(timezone=True), nullable=True)
    
    # Create full-text search index
    __table_args__ = (
        Index(
            'ix_regulations_search',
            search_vector,
            postgresql_using='gin'
        ),
        Index(
            'ix_regulations_category_active',
            'category',
            'active'
        ),
        Index(
            'ix_regulations_created_at',
            'created_at'
        ),
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_search_vector()
    
    def update_search_vector(self):
        """Update the search vector when content changes"""
        if self.title and self.content:
            # This would be handled by a PostgreSQL trigger in production
            # For now, we'll set it to None and let the database handle it
            pass
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
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