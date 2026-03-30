from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


UPLOAD_RESPONSE_EXAMPLE = {
    "document_id": "doc_123",
    "filename": "services-agreement.pdf",
    "content_type": "application/pdf",
    "size_bytes": 48213,
}

SUMMARY_RESPONSE_EXAMPLE = {
    "short_summary": "This appears to be a services agreement with a 12-month initial term.",
    "key_points": [
        "The agreement renews automatically unless notice is given.",
        "Confidentiality obligations continue after termination.",
        "The liability section should be reviewed before signature.",
    ],
}

CLAUSE_RESPONSE_EXAMPLE = {
    "clause_id": "clause_termination",
    "heading": "Termination",
    "category": "termination",
    "extracted_text": "Either party may terminate for material breach with 30 days' notice.",
    "confidence": 0.94,
    "page_reference": 4,
}

RISK_FLAG_RESPONSE_EXAMPLE = {
    "risk_id": "risk_liability_cap",
    "severity": "high",
    "title": "Liability cap is missing",
    "description": "The agreement does not define a clear cap on direct damages.",
    "recommendation": "Add a mutual liability cap tied to fees paid under the agreement.",
    "impacted_clause_id": "clause_liability",
}

ANALYSIS_RESPONSE_EXAMPLE = {
    "document_id": "doc_123",
    "filename": "services-agreement.pdf",
    "document_type": "contract",
    "summary": SUMMARY_RESPONSE_EXAMPLE,
    "clauses": [
        CLAUSE_RESPONSE_EXAMPLE,
    ],
    "risk_flags": [
        RISK_FLAG_RESPONSE_EXAMPLE,
    ],
    "created_at": "2026-03-30T10:00:00Z",
}

RECENT_ANALYSES_RESPONSE_EXAMPLE = {
    "items": [
        {
            "document_id": "doc_123",
            "filename": "services-agreement.pdf",
            "document_type": "contract",
            "created_at": "2026-03-30T10:00:00Z",
        },
        {
            "document_id": "doc_122",
            "filename": "nda.txt",
            "document_type": "contract",
            "created_at": "2026-03-30T09:45:00Z",
        },
    ]
}

ERROR_RESPONSE_EXAMPLE = {
    "error": {
        "code": "not_found",
        "message": "Analysis result was not found.",
    }
}

VALIDATION_ERROR_RESPONSE_EXAMPLE = {
    "error": {
        "code": "validation_error",
        "message": "Request validation failed.",
        "details": [
            {
                "type": "missing",
                "loc": ["body", "file"],
                "msg": "Field required",
                "input": None,
            }
        ],
    }
}


class UploadResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": UPLOAD_RESPONSE_EXAMPLE})

    document_id: str
    filename: str
    content_type: str | None = None
    size_bytes: int


class SummaryResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": SUMMARY_RESPONSE_EXAMPLE})

    short_summary: str
    key_points: list[str] = Field(default_factory=list)


class ClauseResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": CLAUSE_RESPONSE_EXAMPLE})

    clause_id: str
    heading: str
    category: str
    extracted_text: str
    confidence: float
    page_reference: Optional[int] = None


class RiskFlagResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": RISK_FLAG_RESPONSE_EXAMPLE})

    risk_id: str
    severity: str
    title: str
    description: str
    recommendation: str
    impacted_clause_id: Optional[str] = None


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": ANALYSIS_RESPONSE_EXAMPLE})

    document_id: str
    filename: str
    document_type: str
    summary: SummaryResponse
    clauses: list[ClauseResponse] = Field(default_factory=list)
    risk_flags: list[RiskFlagResponse] = Field(default_factory=list)
    created_at: datetime


class RecentAnalysisItem(BaseModel):
    document_id: str
    filename: str
    document_type: str
    created_at: datetime


class RecentAnalysesResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": RECENT_ANALYSES_RESPONSE_EXAMPLE})

    items: list[RecentAnalysisItem] = Field(default_factory=list)


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict[str, object]] | None = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": ERROR_RESPONSE_EXAMPLE})

    error: ErrorDetail
