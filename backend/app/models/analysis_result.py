from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class AnalysisResult(BaseModel):
    """Analysis result model for storing analysis history"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_text: str
    modified_text: str
    llm_comment: str
    change_type: str = Field(..., max_length=50)
    severity: str = Field(..., max_length=50)
    confidence: float = Field(..., ge=0.0, le=1.0)
    
    # Analysis metadata
    analysis_id: str = Field(..., max_length=50)
    document_pair_reference: Optional[str] = Field(None, max_length=500)
    document_pair_client: Optional[str] = Field(None, max_length=500)
    
    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'original_text': self.original_text,
            'modified_text': self.modified_text,
            'llm_comment': self.llm_comment,
            'change_type': self.change_type,
            'severity': self.severity,
            'confidence': self.confidence,
            'analysis_id': self.analysis_id,
            'document_pair_reference': self.document_pair_reference,
            'document_pair_client': self.document_pair_client,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<AnalysisResult(id='{self.id}', severity='{self.severity}', change_type='{self.change_type}')>" 