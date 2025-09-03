from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Optional
import logging
import os
from datetime import datetime
import uuid

from app.database.connection import get_faiss_db
from app.schemas.analysis import AnalysisResponse, CompareDocumentsRequest, ExportRequest
from app.services.document_processor import DocumentProcessor
from app.services.diff_analyzer import DiffAnalyzer
from app.services.regulatory_matcher import RegulatoryMatcher
from app.services.llm_analyzer import LLMAnalyzer
from app.services.report_generator import ReportGenerator
from app.services.metrics import metrics_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
document_processor = DocumentProcessor()
diff_analyzer = DiffAnalyzer()
regulatory_matcher = RegulatoryMatcher()
llm_analyzer = LLMAnalyzer()
report_generator = ReportGenerator()

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой. Максимальный размер: {settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        )
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS_LIST:
        raise HTTPException(
            status_code=415,
            detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(settings.ALLOWED_EXTENSIONS_LIST)}"
        )

async def save_uploaded_file(file: UploadFile) -> str:
    """Save uploaded file and return path"""
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1].lower()
    file_path = os.path.join(settings.UPLOAD_PATH, f"{file_id}.{file_extension}")
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        return file_path
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сохранения файла")

@router.post("/compare", response_model=AnalysisResponse)
async def compare_documents(
    background_tasks: BackgroundTasks,
    reference_doc: UploadFile = File(...),
    client_doc: UploadFile = File(...)
):
    """Compare two documents and analyze changes"""
    
    # Validate files
    validate_file(reference_doc)
    validate_file(client_doc)
    
    analysis_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    try:
        # Save uploaded files
        reference_path = await save_uploaded_file(reference_doc)
        client_path = await save_uploaded_file(client_doc)
        
        logger.info(f"Starting analysis {analysis_id}")
        
        # Process documents
        reference_text = await document_processor.process_document(reference_path)
        client_text = await document_processor.process_document(client_path)
        
        # Analyze differences
        changes = await diff_analyzer.analyze_differences(reference_text, client_text)
        
        # Process each change
        analysis_results = []
        for change in changes:
            # Find relevant regulations
            regulations = await regulatory_matcher.find_relevant_regulations(
                change.text
            )
            
            # Get LLM analysis
            llm_result = await llm_analyzer.analyze_change(
                change, regulations
            )
            
            analysis_results.append({
                "id": str(uuid.uuid4()),
                "originalText": change.original_text,
                "modifiedText": change.modified_text,
                "llmComment": llm_result.comment,
                "requiredServices": llm_result.required_services,
                "changeType": change.change_type,
                "severity": llm_result.severity,
                "confidence": llm_result.confidence,
                "createdAt": datetime.now().isoformat(),
                "highlightedOriginal": change.highlighted_original,
                "highlightedModified": change.highlighted_modified
            })
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Generate summary
        summary = {
            "totalChanges": len(analysis_results),
            "criticalChanges": sum(1 for r in analysis_results if r["severity"] == "critical"),
            "processingTime": f"{processing_time:.2f}s",
            "documentPair": {
                "referenceDoc": reference_doc.filename,
                "clientDoc": client_doc.filename
            }
        }
        
        # Clean up files in background
        background_tasks.add_task(os.remove, reference_path)
        background_tasks.add_task(os.remove, client_path)
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        
        return AnalysisResponse(
            analysisId=analysis_id,
            changes=analysis_results,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error in document analysis: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при анализе документов")

@router.post("/export")
async def export_results(
    request: ExportRequest,
    background_tasks: BackgroundTasks
):
    """Export analysis results to different formats"""
    
    try:
        # Generate report
        report_data = await report_generator.generate_report(
            request.results,
            request.format
        )
        
        # Set appropriate headers
        headers = {
            "Content-Disposition": f"attachment; filename=analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{request.format}"
        }
        
        if request.format == "pdf":
            media_type = "application/pdf"
        elif request.format == "word":
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:  # csv
            media_type = "text/csv"
        
        return StreamingResponse(
            report_data,
            media_type=media_type,
            headers=headers
        )
        
    except Exception as e:
        logger.error(f"Error exporting results: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при экспорте результатов")

@router.get("/regulations")
async def get_regulations(
    skip: int = 0,
    limit: int = 100
):
    """Get list of regulations"""
    
    try:
        regulations = await regulatory_matcher.get_regulations(skip, limit)
        return regulations
        
    except Exception as e:
        logger.error(f"Error fetching regulations: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении нормативных документов")

@router.get("/services")
async def get_services(
    skip: int = 0,
    limit: int = 100
):
    """Get list of services"""
    
    try:
        # This would be implemented based on your service model
        # For now, return a placeholder
        return [
            {"id": "1", "name": "Юридическая служба", "description": "Правовая экспертиза"},
            {"id": "2", "name": "Служба комплаенс", "description": "Соблюдение требований"},
            {"id": "3", "name": "Техническая служба", "description": "Техническая экспертиза"}
        ]
        
    except Exception as e:
        logger.error(f"Error fetching services: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении списка служб")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "document_processor": "running",
            "diff_analyzer": "running",
            "regulatory_matcher": "running",
            "llm_analyzer": "running",
            "report_generator": "running"
        }
    }

@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    from fastapi.responses import Response
    
    try:
        metrics_data = metrics_service.get_metrics()
        return Response(content=metrics_data, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении метрик")

@router.post("/metrics/web-vitals")
async def receive_web_vitals(request: dict):
    """Receive Web Vitals metrics from frontend"""
    try:
        # Validate required fields
        required_fields = ['name', 'value', 'rating', 'delta']
        for field in required_fields:
            if field not in request:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )
        
        # Record the metric
        metrics_service.record_web_vitals(request['name'], request['value'])
        
        # Log the metric for monitoring
        logger.info(f"Web Vitals metric received: {request['name']}={request['value']}, rating={request['rating']}")
        
        # Here you could store metrics in database or send to monitoring system
        # For now, we just log them
        
        return {"status": "success", "message": "Metric received"}
    
    except Exception as e:
        logger.error(f"Error processing web vitals metric: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        ) 