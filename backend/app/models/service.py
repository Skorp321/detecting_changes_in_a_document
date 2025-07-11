from sqlalchemy import Column, String, Text, DateTime, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.database.connection import Base


class Service(Base):
    """Service model for storing approval services/departments"""
    
    __tablename__ = "services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    contact_info = Column(Text, nullable=True)
    approval_type = Column(String(50), default='required', nullable=False)
    
    # Status fields
    active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Create indexes
    __table_args__ = (
        Index('ix_services_name_active', 'name', 'active'),
        Index('ix_services_approval_type', 'approval_type'),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
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