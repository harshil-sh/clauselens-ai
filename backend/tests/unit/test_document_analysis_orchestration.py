from app.domain.models import AnalysisResult, AnalysisSummary, Clause, RiskFlag
from app.repositories.interfaces import AnalysisRepository
from app.services.clause_extraction import ClauseExtractionResult
from app.services.document_analysis import DocumentAnalysisService
from app.services.risk_assessment import RiskAssessmentResult
from app.services.summary_analysis import SummaryAnalysisResult


class RecordingAnalysisRepository(AnalysisRepository):
    def __init__(self) -> None:
        self.saved_results: list[AnalysisResult] = []

    def save(self, result: AnalysisResult) -> AnalysisResult:
        self.saved_results.append(result)
        return result

    def get_by_id(self, document_id: str) -> AnalysisResult | None:
        for result in self.saved_results:
            if result.document_id == document_id:
                return result
        return None

    def list_recent(self) -> list[AnalysisResult]:
        return list(reversed(self.saved_results))


class StubSummaryService:
    def __init__(self, events: list[str]) -> None:
        self._events = events

    def analyze(self, document_text: str) -> SummaryAnalysisResult:
        self._events.append(f"summary:{document_text}")
        return SummaryAnalysisResult(
            document_type="service_agreement",
            summary=AnalysisSummary(
                short_summary="Managed support services agreement.",
                key_points=["One-year term", "30-day termination notice"],
            ),
        )


class StubClauseService:
    def __init__(self, events: list[str], clauses: list[Clause]) -> None:
        self._events = events
        self._clauses = clauses

    def analyze(self, document_text: str) -> ClauseExtractionResult:
        self._events.append(f"clauses:{document_text}")
        return ClauseExtractionResult(clauses=self._clauses)


class StubRiskService:
    def __init__(self, events: list[str], expected_clauses: list[Clause]) -> None:
        self._events = events
        self._expected_clauses = expected_clauses

    def analyze(self, document_text: str, clauses: list[Clause]) -> RiskAssessmentResult:
        assert clauses == self._expected_clauses
        self._events.append(f"risks:{document_text}:{clauses[0].clause_id}")
        return RiskAssessmentResult(
            risk_flags=[
                RiskFlag(
                    risk_id="risk_1",
                    severity="medium",
                    title="Liability cap missing",
                    description="The contract does not clearly cap supplier liability.",
                    recommendation="Add an explicit liability cap.",
                    impacted_clause_id=clauses[0].clause_id,
                )
            ]
        )


def test_document_analysis_service_orchestrates_full_analysis_and_persists_result() -> None:
    events: list[str] = []
    repository = RecordingAnalysisRepository()
    clauses = [
        Clause(
            clause_id="clause_1",
            heading="Liability",
            category="liability",
            extracted_text="Supplier liability is unlimited.",
            confidence=0.88,
        )
    ]
    service = DocumentAnalysisService(
        repository=repository,
        summary_service=StubSummaryService(events),
        clause_service=StubClauseService(events, clauses),
        risk_service=StubRiskService(events, clauses),
    )

    result = service.analyse(
        filename="msa.txt",
        document_text="Managed services agreement text",
    )

    assert events == [
        "summary:Managed services agreement text",
        "clauses:Managed services agreement text",
        "risks:Managed services agreement text:clause_1",
    ]
    assert result.filename == "msa.txt"
    assert result.document_type == "service_agreement"
    assert result.summary.short_summary == "Managed support services agreement."
    assert result.summary.key_points == ["One-year term", "30-day termination notice"]
    assert result.clauses == clauses
    assert result.risk_flags[0].impacted_clause_id == "clause_1"
    assert result.document_id.startswith("doc_")
    assert repository.saved_results == [result]


def test_document_analysis_service_requires_openai_client_or_explicit_subservices() -> None:
    repository = RecordingAnalysisRepository()

    try:
        DocumentAnalysisService(repository=repository)
    except ValueError as exc:
        assert "requires an openai_client" in str(exc)
    else:
        raise AssertionError("Expected a ValueError when orchestration dependencies are missing.")
