from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    filename: str
    content_type: str | None = None
    size_bytes: int


class SummaryResponse(BaseModel):
    short_summary: str
    key_points: list[str] = Field(default_factory=list)


class ClauseResponse(BaseModel):
    clause_id: str
    heading: str
    category: str
    extracted_text: str
    confidence: float
    page_reference: Optional[int] = None


class RiskFlagResponse(BaseModel):
    risk_id: str
    severity: str
    title: str
    description: str
    recommendation: str
    impacted_clause_id: Optional[str] = None


class AnalysisResponse(BaseModel):
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
    items: list[RecentAnalysisItem] = Field(default_factory=list)
