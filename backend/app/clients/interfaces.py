from __future__ import annotations

from typing import Protocol, TypedDict


class SummaryPayload(TypedDict):
    document_type: str
    short_summary: str
    key_points: list[str]


class ExtractedClausePayload(TypedDict, total=False):
    heading: str
    category: str
    extracted_text: str
    confidence: float
    page_reference: int | None


class ClauseExtractionPayload(TypedDict):
    clauses: list[ExtractedClausePayload]


class ClauseContext(TypedDict):
    clause_id: str
    heading: str
    category: str
    extracted_text: str


class RiskFlagPayload(TypedDict, total=False):
    severity: str
    title: str
    description: str
    recommendation: str
    impacted_clause_id: str | None


class RiskAssessmentPayload(TypedDict):
    risk_flags: list[RiskFlagPayload]


class DocumentAnalysisAIClient(Protocol):
    def summarize(self, document_text: str) -> SummaryPayload:
        ...

    def extract_clauses(self, document_text: str) -> ClauseExtractionPayload:
        ...

    def assess_risks(
        self,
        document_text: str,
        clauses: list[ClauseContext],
    ) -> RiskAssessmentPayload:
        ...
