from __future__ import annotations

from uuid import uuid4

from app.domain.models import AnalysisResult, AnalysisSummary, Clause, RiskFlag
from app.repositories.interfaces import AnalysisRepository
from app.services.openai_client import OpenAIClient


class DocumentAnalysisService:
    def __init__(self, repository: AnalysisRepository, openai_client: OpenAIClient) -> None:
        self.repository = repository
        self.openai_client = openai_client

    def analyse(self, filename: str, document_text: str) -> AnalysisResult:
        summary_payload = self.openai_client.summarize(document_text)
        clauses_payload = self.openai_client.extract_clauses(document_text)

        clauses = [
            Clause(
                clause_id=f"clause_{index + 1}",
                heading=item["heading"],
                category=item["category"],
                extracted_text=item["extracted_text"],
                confidence=float(item.get("confidence", 0.0)),
                page_reference=item.get("page_reference"),
            )
            for index, item in enumerate(clauses_payload.get("clauses", []))
        ]

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
            document_type=summary_payload.get("document_type", "unknown"),
            summary=AnalysisSummary(
                short_summary=summary_payload.get("short_summary", ""),
                key_points=list(summary_payload.get("key_points", [])),
            ),
            clauses=clauses,
            risk_flags=risk_flags,
        )
        return self.repository.save(result)

    def get_by_id(self, document_id: str) -> AnalysisResult | None:
        return self.repository.get_by_id(document_id)

    def list_recent(self) -> list[AnalysisResult]:
        return self.repository.list_recent()
