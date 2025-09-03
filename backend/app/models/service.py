from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Service(BaseModel):
    """Service model for storing approval services/departments"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    contact_info: Optional[str] = None
    approval_type: str = Field(default='required', max_length=50)
    
    # Status fields
    active: bool = True
    
    # Metadata
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'contact_info': self.contact_info,
            'approval_type': self.approval_type,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f"<Service(id='{self.id}', name='{self.name}', active={self.active})>" 