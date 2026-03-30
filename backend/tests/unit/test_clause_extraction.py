from app.domain.models import Clause
from app.services.clause_extraction import (
    ClauseExtractionService,
    ClauseMappingError,
    ClauseResponseMapper,
)


class StubClauseAIClient:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload
        self.calls: list[str] = []

    def extract_clauses(self, document_text: str) -> dict[str, object]:
        self.calls.append(document_text)
        return self.payload


def test_clause_response_mapper_normalizes_clause_payload() -> None:
    mapper = ClauseResponseMapper()

    result = mapper.map(
        {
            "clauses": [
                {
                    "heading": "  Data handling  ",
                    "category": " Data Protection ",
                    "extracted_text": "  Provider must encrypt personal data at rest.  ",
                    "confidence": 1.4,
                    "page_reference": 0,
                },
                {
                    "heading": " ",
                    "category": "Custom Category",
                    "extracted_text": " Customer must approve subcontractors in writing. ",
                },
            ]
        }
    )

    assert result.clauses == [
        Clause(
            clause_id="clause_1",
            heading="Data handling",
            category="data_protection",
            extracted_text="Provider must encrypt personal data at rest.",
            confidence=1.0,
            page_reference=None,
        ),
        Clause(
            clause_id="clause_2",
            heading="Clause 2",
            category="other",
            extracted_text="Customer must approve subcontractors in writing.",
            confidence=0.0,
            page_reference=None,
        ),
    ]


def test_clause_response_mapper_rejects_blank_extracted_text() -> None:
    mapper = ClauseResponseMapper()

    try:
        mapper.map(
            {
                "clauses": [
                    {
                        "heading": "Termination",
                        "category": "termination",
                        "extracted_text": "   ",
                    }
                ]
            }
        )
    except ClauseMappingError as exc:
        assert "extracted_text" in str(exc)
    else:
        raise AssertionError("Expected a ClauseMappingError for blank extracted_text.")


def test_clause_extraction_service_uses_ai_client_and_mapper() -> None:
    client = StubClauseAIClient(
        {
            "clauses": [
                {
                    "heading": "Renewal",
                    "category": "term",
                    "extracted_text": "The agreement renews automatically for one-year periods.",
                    "confidence": 0.82,
                    "page_reference": 3,
                }
            ]
        }
    )
    service = ClauseExtractionService(openai_client=client)

    result = service.analyze("Agreement text")

    assert client.calls == ["Agreement text"]
    assert result.clauses == [
        Clause(
            clause_id="clause_1",
            heading="Renewal",
            category="term",
            extracted_text="The agreement renews automatically for one-year periods.",
            confidence=0.82,
            page_reference=3,
        )
    ]
