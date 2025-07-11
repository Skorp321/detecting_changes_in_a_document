from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ChangeType(str, Enum):
    """Types of changes detected"""
    ADDITION = "addition"
    DELETION = "deletion"
    MODIFICATION = "modification"


class Severity(str, Enum):
    """Severity levels for changes"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExportFormat(str, Enum):
    """Export formats supported"""
    CSV = "csv"
    PDF = "pdf"
    WORD = "word"


class AnalysisResult(BaseModel):
    """Analysis result for a single change"""
    id: str = Field(..., description="Unique identifier for the change")
    originalText: str = Field(..., description="Original text from reference document")
    modifiedText: str = Field(..., description="Modified text from client document")
    llmComment: str = Field(..., description="LLM analysis comment")
    requiredServices: List[str] = Field(..., description="Required approval services")
    changeType: ChangeType = Field(..., description="Type of change")
    severity: Severity = Field(..., description="Severity level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    createdAt: str = Field(..., description="Creation timestamp")
    highlightedOriginal: Optional[str] = Field(None, description="Original text with highlighted changes")
    highlightedModified: Optional[str] = Field(None, description="Modified text with highlighted changes")


class DocumentPair(BaseModel):
    """Document pair information"""
    referenceDoc: str = Field(..., description="Reference document filename")
    clientDoc: str = Field(..., description="Client document filename")


class AnalysisSummary(BaseModel):
    """Summary of analysis results"""
    totalChanges: int = Field(..., description="Total number of changes detected")
    criticalChanges: int = Field(..., description="Number of critical changes")
    processingTime: str = Field(..., description="Processing time in seconds")
    documentPair: DocumentPair = Field(..., description="Document pair information")


class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    analysisId: str = Field(..., description="Unique analysis identifier")
    changes: List[AnalysisResult] = Field(..., description="List of detected changes")
    summary: AnalysisSummary = Field(..., description="Analysis summary")


class CompareDocumentsRequest(BaseModel):
    """Request for document comparison"""
    referenceDoc: str = Field(..., description="Reference document path")
    clientDoc: str = Field(..., description="Client document path")
    options: Optional[Dict[str, Any]] = Field(None, description="Analysis options")


class ExportRequest(BaseModel):
    """Request for exporting analysis results"""
    results: List[AnalysisResult] = Field(..., description="Analysis results to export")
    format: ExportFormat = Field(..., description="Export format")
    includeMetadata: bool = Field(True, description="Include metadata in export")
    filename: Optional[str] = Field(None, description="Custom filename")


class FileUploadResponse(BaseModel):
    """Response for file upload"""
    success: bool = Field(..., description="Upload success status")
    filename: str = Field(..., description="Uploaded filename")
    fileId: str = Field(..., description="Unique file identifier")
    size: int = Field(..., description="File size in bytes")
    message: Optional[str] = Field(None, description="Status message")


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error description")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ValidationError(BaseModel):
    """Validation error details"""
    field: str = Field(..., description="Field with validation error")
    message: str = Field(..., description="Validation error message")
    value: Optional[Any] = Field(None, description="Invalid value")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Check timestamp")
    version: str = Field(..., description="Service version")
    services: Dict[str, str] = Field(..., description="Service statuses")


class RegulationInfo(BaseModel):
    """Regulation information"""
    id: str = Field(..., description="Regulation ID")
    title: str = Field(..., description="Regulation title")
    content: str = Field(..., description="Regulation content")
    category: str = Field(..., description="Regulation category")
    services: List[str] = Field(..., description="Associated services")
    createdAt: str = Field(..., description="Creation timestamp")
    updatedAt: str = Field(..., description="Last update timestamp")


class ServiceInfo(BaseModel):
    """Service information"""
    id: str = Field(..., description="Service ID")
    name: str = Field(..., description="Service name")
    description: str = Field(..., description="Service description")
    contactInfo: str = Field(..., description="Contact information")
    approvalType: str = Field(..., description="Approval type")
    active: bool = Field(..., description="Service active status")


class DocumentInfo(BaseModel):
    """Document information"""
    filename: str = Field(..., description="Document filename")
    size: int = Field(..., description="Document size in bytes")
    type: str = Field(..., description="Document type")
    pages: Optional[int] = Field(None, description="Number of pages")
    language: Optional[str] = Field(None, description="Document language")
    encoding: Optional[str] = Field(None, description="Text encoding")


class ProcessingStatus(BaseModel):
    """Processing status information"""
    status: str = Field(..., description="Current processing status")
    progress: float = Field(..., ge=0.0, le=1.0, description="Processing progress")
    message: Optional[str] = Field(None, description="Status message")
    estimatedTimeRemaining: Optional[int] = Field(None, description="Estimated time remaining in seconds")


class AnalysisConfig(BaseModel):
    """Analysis configuration"""
    includeMinorChanges: bool = Field(True, description="Include minor changes")
    confidenceThreshold: float = Field(0.5, ge=0.0, le=1.0, description="Confidence threshold")
    maxProcessingTime: int = Field(300, description="Maximum processing time in seconds")
    language: str = Field("ru", description="Analysis language")
    batchSize: int = Field(10, description="Batch size for processing")


class LLMAnalysisResult(BaseModel):
    """LLM analysis result"""
    comment: str = Field(..., description="LLM analysis comment")
    requiredServices: List[str] = Field(..., description="Required services")
    severity: Severity = Field(..., description="Severity assessment")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reasoning: Optional[str] = Field(None, description="Analysis reasoning")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations")


class DiffChange(BaseModel):
    """Individual difference change"""
    originalText: str = Field(..., description="Original text")
    modifiedText: str = Field(..., description="Modified text")
    changeType: ChangeType = Field(..., description="Type of change")
    position: int = Field(..., description="Position in document")
    context: Optional[str] = Field(None, description="Surrounding context")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score") 