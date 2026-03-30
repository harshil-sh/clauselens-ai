from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import (
    get_document_analysis_service,
    get_file_validation_service,
    get_local_upload_storage_service,
    get_uploaded_document_text_extraction_service,
)
from app.core.errors import ApiError
from app.schemas.document import (
    ANALYSIS_RESPONSE_EXAMPLE,
    ERROR_RESPONSE_EXAMPLE,
    RECENT_ANALYSES_RESPONSE_EXAMPLE,
    UPLOAD_RESPONSE_EXAMPLE,
    VALIDATION_ERROR_RESPONSE_EXAMPLE,
    AnalysisResponse,
    ErrorResponse,
    RecentAnalysesResponse,
    UploadResponse,
)
from app.services.document_analysis import DocumentAnalysisService
from app.services.file_validation import FileValidationService
from app.services.text_extraction import UploadedDocumentTextExtractionService
from app.services.upload_storage import LocalUploadStorageService

router = APIRouter(prefix="/documents", tags=["documents"])

MULTIPART_FILE_REQUEST_BODY = {
    "content": {
        "multipart/form-data": {
            "schema": {
                "type": "object",
                "required": ["file"],
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                        "description": "Contract document file in PDF, DOCX, or TXT format.",
                    }
                },
            }
        }
    }
}

DOCUMENT_UPLOAD_RESPONSES = {
    200: {
        "description": "Document uploaded successfully.",
        "content": {
            "application/json": {
                "example": UPLOAD_RESPONSE_EXAMPLE,
            }
        },
    },
    422: {
        "model": ErrorResponse,
        "description": "The upload request is invalid.",
        "content": {
            "application/json": {
                "examples": {
                    "validation_error": {
                        "summary": "Missing file field",
                        "value": VALIDATION_ERROR_RESPONSE_EXAMPLE,
                    }
                }
            }
        },
    },
}

ANALYSIS_RESPONSES = {
    200: {
        "description": "Structured analysis result for the uploaded document.",
        "content": {
            "application/json": {
                "example": ANALYSIS_RESPONSE_EXAMPLE,
            }
        },
    },
    422: {
        "model": ErrorResponse,
        "description": "The analysis request is invalid.",
        "content": {
            "application/json": {
                "examples": {
                    "validation_error": {
                        "summary": "Missing file field",
                        "value": VALIDATION_ERROR_RESPONSE_EXAMPLE,
                    }
                }
            }
        },
    },
}

GET_ANALYSIS_RESPONSES = {
    200: {
        "description": "Previously saved analysis result.",
        "content": {
            "application/json": {
                "example": ANALYSIS_RESPONSE_EXAMPLE,
            }
        },
    },
    404: {
        "model": ErrorResponse,
        "description": "No analysis exists for the supplied document id.",
        "content": {
            "application/json": {
                "examples": {
                    "not_found": {
                        "summary": "Unknown document id",
                        "value": ERROR_RESPONSE_EXAMPLE,
                    }
                }
            }
        },
    },
}

LIST_ANALYSES_RESPONSES = {
    200: {
        "description": "Most recent saved analyses, newest first.",
        "content": {
            "application/json": {
                "example": RECENT_ANALYSES_RESPONSE_EXAMPLE,
            }
        },
    }
}


def _build_analysis_response(result) -> AnalysisResponse:
    return AnalysisResponse.model_validate(result.__dict__ | {
        "summary": result.summary.__dict__,
        "clauses": [clause.__dict__ for clause in result.clauses],
        "risk_flags": [risk.__dict__ for risk in result.risk_flags],
    })


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload a document",
    description="Stores a validated document and returns the generated document identifier.",
    responses=DOCUMENT_UPLOAD_RESPONSES,
    openapi_extra={"requestBody": MULTIPART_FILE_REQUEST_BODY},
)
async def upload_document(
    file: UploadFile = File(...),
    validation_service: FileValidationService = Depends(get_file_validation_service),
    storage_service: LocalUploadStorageService = Depends(get_local_upload_storage_service),
) -> UploadResponse:
    validated = await validation_service.validate_upload(file)
    stored = storage_service.store(validated)
    return UploadResponse(
        document_id=stored.document_id,
        filename=stored.filename,
        content_type=stored.content_type,
        size_bytes=stored.size_bytes,
    )


@router.post(
    "/analyse",
    response_model=AnalysisResponse,
    summary="Analyse a document",
    description=(
        "Validates an uploaded document, extracts text, and returns a structured contract "
        "analysis with summary, clauses, and risk flags."
    ),
    responses=ANALYSIS_RESPONSES,
    openapi_extra={"requestBody": MULTIPART_FILE_REQUEST_BODY},
)
async def analyse_document(
    file: UploadFile = File(...),
    validation_service: FileValidationService = Depends(get_file_validation_service),
    extraction_service: UploadedDocumentTextExtractionService = Depends(
        get_uploaded_document_text_extraction_service
    ),
    service: DocumentAnalysisService = Depends(get_document_analysis_service),
) -> AnalysisResponse:
    validated = await validation_service.validate_upload(file)
    extracted = extraction_service.extract(validated)
    result = service.analyse(filename=validated.filename, document_text=extracted.extracted_text)
    return _build_analysis_response(result)


@router.get(
    "/{document_id}",
    response_model=AnalysisResponse,
    summary="Get analysis by document id",
    description="Returns a previously saved analysis result for the supplied document identifier.",
    responses=GET_ANALYSIS_RESPONSES,
)
async def get_document_analysis(
    document_id: str,
    service: DocumentAnalysisService = Depends(get_document_analysis_service),
) -> AnalysisResponse:
    result = service.get_by_id(document_id)
    if result is None:
        raise ApiError(code="not_found", message="Analysis result was not found.", status_code=404)
    return _build_analysis_response(result)


@router.get(
    "",
    response_model=RecentAnalysesResponse,
    summary="List recent analyses",
    description="Returns previously saved analysis results ordered from newest to oldest.",
    responses=LIST_ANALYSES_RESPONSES,
)
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
