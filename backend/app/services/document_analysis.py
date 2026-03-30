from __future__ import annotations

from uuid import uuid4

from app.clients.interfaces import DocumentAnalysisAIClient
from app.domain.models import AnalysisResult, AnalysisSummary
from app.repositories.interfaces import AnalysisRepository
from app.services.clause_extraction import ClauseExtractionService, ClauseExtractionResult
from app.services.risk_assessment import RiskAssessmentResult, RiskAssessmentService
from app.services.summary_analysis import SummaryAnalysisResult, SummaryAnalysisService


class DocumentAnalysisService:
    def __init__(
        self,
        repository: AnalysisRepository,
        openai_client: DocumentAnalysisAIClient | None = None,
        summary_service: SummaryAnalysisService | None = None,
        clause_service: ClauseExtractionService | None = None,
        risk_service: RiskAssessmentService | None = None,
    ) -> None:
        if openai_client is None and (
            summary_service is None or clause_service is None or risk_service is None
        ):
            raise ValueError(
                "DocumentAnalysisService requires an openai_client or explicit summary, clause, and risk services."
            )

        self.repository = repository
        self.summary_service = summary_service or SummaryAnalysisService(openai_client=openai_client)
        self.clause_service = clause_service or ClauseExtractionService(openai_client=openai_client)
        self.risk_service = risk_service or RiskAssessmentService(openai_client=openai_client)

    def analyse(self, filename: str, document_text: str) -> AnalysisResult:
        summary_result = self.summary_service.analyze(document_text)
        clause_result = self.clause_service.analyze(document_text)
        clauses = clause_result.clauses
        risk_result = self.risk_service.analyze(document_text, clauses)

        result = self._build_analysis_result(
            filename=filename,
            summary_result=summary_result,
            clause_result=clause_result,
            risk_result=risk_result,
        )
        return self.repository.save(result)

    def _build_analysis_result(
        self,
        *,
        filename: str,
        summary_result: SummaryAnalysisResult,
        clause_result: ClauseExtractionResult,
        risk_result: RiskAssessmentResult,
    ) -> AnalysisResult:
        return AnalysisResult(
            document_id=f"doc_{uuid4().hex[:12]}",
            filename=filename,
            document_type=summary_result.document_type,
            summary=AnalysisSummary(
                short_summary=summary_result.summary.short_summary,
                key_points=list(summary_result.summary.key_points),
            ),
            clauses=list(clause_result.clauses),
            risk_flags=risk_result.risk_flags,
        )

    def get_by_id(self, document_id: str) -> AnalysisResult | None:
        return self.repository.get_by_id(document_id)

    def list_recent(self) -> list[AnalysisResult]:
        return self.repository.list_recent()
