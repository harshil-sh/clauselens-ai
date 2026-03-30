from __future__ import annotations

from uuid import uuid4

from app.clients.interfaces import DocumentAnalysisAIClient
from app.domain.models import AnalysisResult, AnalysisSummary, RiskFlag
from app.repositories.interfaces import AnalysisRepository
from app.services.clause_extraction import ClauseExtractionService
from app.services.summary_analysis import SummaryAnalysisService


class DocumentAnalysisService:
    def __init__(self, repository: AnalysisRepository, openai_client: DocumentAnalysisAIClient) -> None:
        self.repository = repository
        self.openai_client = openai_client
        self.summary_service = SummaryAnalysisService(openai_client=openai_client)
        self.clause_service = ClauseExtractionService(openai_client=openai_client)

    def analyse(self, filename: str, document_text: str) -> AnalysisResult:
        summary_result = self.summary_service.analyze(document_text)
        clause_result = self.clause_service.analyze(document_text)
        clauses = clause_result.clauses

        risks_payload = self.openai_client.assess_risks(
            document_text,
            [
                {
                    "clause_id": clause.clause_id,
                    "heading": clause.heading,
                    "category": clause.category,
                    "extracted_text": clause.extracted_text,
                }
                for clause in clauses
            ],
        )

        risk_flags = [
            RiskFlag(
                risk_id=f"risk_{index + 1}",
                severity=item["severity"],
                title=item["title"],
                description=item["description"],
                recommendation=item["recommendation"],
                impacted_clause_id=item.get("impacted_clause_id"),
            )
            for index, item in enumerate(risks_payload.get("risk_flags", []))
        ]

        result = AnalysisResult(
            document_id=f"doc_{uuid4().hex[:12]}",
            filename=filename,
            document_type=summary_result.document_type,
            summary=AnalysisSummary(
                short_summary=summary_result.summary.short_summary,
                key_points=list(summary_result.summary.key_points),
            ),
            clauses=clauses,
            risk_flags=risk_flags,
        )
        return self.repository.save(result)

    def get_by_id(self, document_id: str) -> AnalysisResult | None:
        return self.repository.get_by_id(document_id)

    def list_recent(self) -> list[AnalysisResult]:
        return self.repository.list_recent()
