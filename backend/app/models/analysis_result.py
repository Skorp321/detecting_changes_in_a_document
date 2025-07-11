from sqlalchemy import Column, String, Text, DateTime, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.database.connection import Base


class AnalysisResult(Base):
    """Analysis result model for storing analysis history"""
    
    __tablename__ = "analysis_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_text = Column(Text, nullable=False)
    modified_text = Column(Text, nullable=False)
    llm_comment = Column(Text, nullable=False)
    change_type = Column(String(50), nullable=False)
    severity = Column(String(50), nullable=False)
    confidence = Column(Numeric(3, 2), nullable=False)
    
    # Analysis metadata
    analysis_id = Column(UUID(as_uuid=True), nullable=False)
    document_pair_reference = Column(String(500), nullable=True)
    document_pair_client = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Create indexes
    __table_args__ = (
        Index('ix_analysis_results_analysis_id', 'analysis_id'),
        Index('ix_analysis_results_severity', 'severity'),
        Index('ix_analysis_results_change_type', 'change_type'),
        Index('ix_analysis_results_created_at', 'created_at'),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'original_text': self.original_text,
            'modified_text': self.modified_text,
            'llm_comment': self.llm_comment,
            'change_type': self.change_type,
            'severity': self.severity,
            'confidence': float(self.confidence),
            'analysis_id': str(self.analysis_id),
            'document_pair_reference': self.document_pair_reference,
            'document_pair_client': self.document_pair_client,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<AnalysisResult(id='{self.id}', severity='{self.severity}', change_type='{self.change_type}')>" 