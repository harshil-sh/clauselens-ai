from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_document_analysis_service, get_file_validation_service
from app.core.errors import ApiError
from app.schemas.document import AnalysisResponse, RecentAnalysesResponse, UploadResponse
from app.services.document_analysis import DocumentAnalysisService
from app.services.file_validation import FileValidationService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    validation_service: FileValidationService = Depends(get_file_validation_service),
) -> UploadResponse:
    validated = await validation_service.validate_upload(file)
    return UploadResponse(
        filename=validated.filename,
        content_type=validated.content_type,
        size_bytes=validated.size_bytes,
    )


@router.post("/analyse", response_model=AnalysisResponse)
async def analyse_document(
    file: UploadFile = File(...),
    service: DocumentAnalysisService = Depends(get_document_analysis_service),
) -> AnalysisResponse:
    if not file.filename:
        raise ApiError(code="missing_filename", message="Uploaded file must have a filename.", status_code=400)

    file_bytes = await file.read()
    if not file_bytes:
        raise ApiError(code="empty_file", message="Uploaded file is empty.", status_code=400)

    document_text = file_bytes.decode("utf-8", errors="ignore")
    result = service.analyse(filename=file.filename, document_text=document_text)
    return AnalysisResponse.model_validate(result.__dict__ | {
        "summary": result.summary.__dict__,
        "clauses": [clause.__dict__ for clause in result.clauses],
        "risk_flags": [risk.__dict__ for risk in result.risk_flags],
    })


@router.get("/{document_id}", response_model=AnalysisResponse)
def get_document_analysis(
    document_id: str,
    service: DocumentAnalysisService = Depends(get_document_analysis_service),
) -> AnalysisResponse:
    result = service.get_by_id(document_id)
    if result is None:
        raise ApiError(code="not_found", message="Analysis result was not found.", status_code=404)
    return AnalysisResponse.model_validate(result.__dict__ | {
        "summary": result.summary.__dict__,
        "clauses": [clause.__dict__ for clause in result.clauses],
        "risk_flags": [risk.__dict__ for risk in result.risk_flags],
    })


@router.get("", response_model=RecentAnalysesResponse)
def list_recent_analyses(
    service: DocumentAnalysisService = Depends(get_document_analysis_service),
) -> RecentAnalysesResponse:
    items = service.list_recent()
    return RecentAnalysesResponse(
        items=[
            {
                "document_id": item.document_id,
                "filename": item.filename,
                "document_type": item.document_type,
                "created_at": item.created_at,
            }
            for item in items
        ]
    )
