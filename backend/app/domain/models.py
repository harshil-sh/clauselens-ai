from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Clause:
    clause_id: str
    heading: str
    category: str
    extracted_text: str
    confidence: float
    page_reference: Optional[int] = None


@dataclass
class RiskFlag:
    risk_id: str
    severity: str
    title: str
    description: str
    recommendation: str
    impacted_clause_id: Optional[str] = None


@dataclass
class AnalysisSummary:
    short_summary: str
    key_points: list[str] = field(default_factory=list)


@dataclass
class DocumentRecord:
    document_id: str
    filename: str
    content_type: str | None = None
    storage_path: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExtractedDocument:
    filename: str
    file_extension: str
    extracted_text: str
    char_count: int


@dataclass
class AnalysisResult:
    document_id: str
    filename: str
    document_type: str
    summary: AnalysisSummary
    clauses: list[Clause] = field(default_factory=list)
    risk_flags: list[RiskFlag] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
