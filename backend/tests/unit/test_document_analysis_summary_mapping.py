from app.clients.interfaces import ClauseExtractionPayload, ClauseContext, RiskAssessmentPayload, SummaryPayload
from app.repositories.in_memory import InMemoryAnalysisRepository
from app.services.document_analysis import DocumentAnalysisService


class StubDocumentAnalysisAIClient:
    def summarize(self, document_text: str) -> SummaryPayload:
        return {
            "document_type": " Service Agreement ",
            "short_summary": "  This document sets out support services. ",
            "key_points": [
                " Annual term ",
                "Annual term",
                "Termination for breach",
            ],
        }

    def extract_clauses(self, document_text: str) -> ClauseExtractionPayload:
        return {
            "clauses": [
                {
                    "heading": "Term",
                    "category": "term",
                    "extracted_text": "The agreement runs for one year.",
                }
            ]
        }

    def assess_risks(
        self,
        document_text: str,
        clauses: list[ClauseContext],
    ) -> RiskAssessmentPayload:
        return {
            "risk_flags": [
                {
                    "severity": "low",
                    "title": "Renewal terms need review",
                    "description": "Auto-renewal language is not explicit.",
                    "recommendation": "Confirm whether renewal should be automatic.",
                    "impacted_clause_id": clauses[0]["clause_id"],
                }
            ]
        }


def test_document_analysis_service_applies_summary_mapping() -> None:
    service = DocumentAnalysisService(
        repository=InMemoryAnalysisRepository(),
        openai_client=StubDocumentAnalysisAIClient(),
    )

    result = service.analyse(
        filename="agreement.txt",
        document_text="Agreement text",
    )

    assert result.document_type == "service_agreement"
    assert result.summary.short_summary == "This document sets out support services."
    assert result.summary.key_points == ["Annual term", "Termination for breach"]
    assert result.clauses[0].clause_id == "clause_1"
    assert result.clauses[0].heading == "Term"
    assert result.clauses[0].category == "term"
    assert result.clauses[0].extracted_text == "The agreement runs for one year."
    assert result.risk_flags[0].impacted_clause_id == "clause_1"
