from app.domain.models import AnalysisSummary
from app.services.summary_analysis import (
    SummaryAnalysisService,
    SummaryMappingError,
    SummaryResponseMapper,
)


class StubSummaryAIClient:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload
        self.calls: list[str] = []

    def summarize(self, document_text: str) -> dict[str, object]:
        self.calls.append(document_text)
        return self.payload


def test_summary_response_mapper_normalizes_summary_payload() -> None:
    mapper = SummaryResponseMapper()

    result = mapper.map(
        {
            "document_type": "  Service Agreement  ",
            "short_summary": "  This agreement covers managed support services.  ",
            "key_points": [
                " 12-month initial term ",
                "",
                "12-month initial term",
                "Customer may terminate for breach",
            ],
        }
    )

    assert result.document_type == "service_agreement"
    assert result.summary == AnalysisSummary(
        short_summary="This agreement covers managed support services.",
        key_points=[
            "12-month initial term",
            "Customer may terminate for breach",
        ],
    )


def test_summary_response_mapper_rejects_blank_short_summary() -> None:
    mapper = SummaryResponseMapper()

    try:
        mapper.map(
            {
                "document_type": "contract",
                "short_summary": "   ",
                "key_points": [],
            }
        )
    except SummaryMappingError as exc:
        assert "short_summary" in str(exc)
    else:
        raise AssertionError("Expected a SummaryMappingError for blank short_summary.")


def test_summary_analysis_service_uses_ai_client_and_mapper() -> None:
    client = StubSummaryAIClient(
        {
            "document_type": "Policy Memo",
            "short_summary": "Internal policy update.",
            "key_points": ["New retention rules"],
        }
    )
    service = SummaryAnalysisService(openai_client=client)

    result = service.analyze("Policy text")

    assert client.calls == ["Policy text"]
    assert result.document_type == "policy_memo"
    assert result.summary == AnalysisSummary(
        short_summary="Internal policy update.",
        key_points=["New retention rules"],
    )
