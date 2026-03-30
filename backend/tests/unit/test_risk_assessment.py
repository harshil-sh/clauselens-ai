from app.domain.models import Clause, RiskFlag
from app.services.risk_assessment import (
    RiskAssessmentService,
    RiskMappingError,
    RiskResponseMapper,
)


class StubRiskAIClient:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload
        self.calls: list[tuple[str, list[dict[str, str]]]] = []

    def assess_risks(self, document_text: str, clauses: list[dict[str, str]]) -> dict[str, object]:
        self.calls.append((document_text, clauses))
        return self.payload


def test_risk_response_mapper_normalizes_risk_payload() -> None:
    mapper = RiskResponseMapper()

    result = mapper.map(
        {
            "risk_flags": [
                {
                    "severity": " High ",
                    "title": "  Broad indemnity exposure ",
                    "description": " Provider indemnifies all third-party claims without cap. ",
                    "recommendation": " Narrow the indemnity scope and add a liability cap. ",
                    "impacted_clause_id": " clause_2 ",
                },
                {
                    "severity": "low",
                    "title": " Missing audit right ",
                    "description": " No explicit audit mechanism is described. ",
                    "recommendation": " Add an audit clause if oversight is required. ",
                    "impacted_clause_id": "unknown_clause",
                },
            ]
        },
        valid_clause_ids={"clause_1", "clause_2"},
    )

    assert result.risk_flags == [
        RiskFlag(
            risk_id="risk_1",
            severity="high",
            title="Broad indemnity exposure",
            description="Provider indemnifies all third-party claims without cap.",
            recommendation="Narrow the indemnity scope and add a liability cap.",
            impacted_clause_id="clause_2",
        ),
        RiskFlag(
            risk_id="risk_2",
            severity="low",
            title="Missing audit right",
            description="No explicit audit mechanism is described.",
            recommendation="Add an audit clause if oversight is required.",
            impacted_clause_id=None,
        ),
    ]


def test_risk_response_mapper_rejects_invalid_severity() -> None:
    mapper = RiskResponseMapper()

    try:
        mapper.map(
            {
                "risk_flags": [
                    {
                        "severity": "critical",
                        "title": "Unlimited liability",
                        "description": "The contract lacks a liability cap.",
                        "recommendation": "Add a cap.",
                    }
                ]
            },
            valid_clause_ids=set(),
        )
    except RiskMappingError as exc:
        assert "severity" in str(exc)
    else:
        raise AssertionError("Expected a RiskMappingError for invalid severity.")


def test_risk_response_mapper_skips_malformed_risk_entries() -> None:
    mapper = RiskResponseMapper()

    result = mapper.map(
        {
            "risk_flags": [
                {
                    "severity": "high",
                    "title": "Unlimited liability",
                    "description": "The contract does not cap supplier liability.",
                    "recommendation": "Add a liability cap.",
                    "impacted_clause_id": "clause_1",
                },
                {
                    "severity": "critical",
                    "title": "Invalid severity",
                    "description": "This item should be skipped.",
                    "recommendation": "Ignore it.",
                },
                {
                    "severity": "low",
                    "title": " ",
                    "description": "This item is missing a title.",
                    "recommendation": "Ignore it too.",
                },
            ]
        },
        valid_clause_ids={"clause_1"},
    )

    assert result.risk_flags == [
        RiskFlag(
            risk_id="risk_1",
            severity="high",
            title="Unlimited liability",
            description="The contract does not cap supplier liability.",
            recommendation="Add a liability cap.",
            impacted_clause_id="clause_1",
        )
    ]


def test_risk_assessment_service_uses_ai_client_and_mapper() -> None:
    client = StubRiskAIClient(
        {
            "risk_flags": [
                {
                    "severity": " medium ",
                    "title": " Renewal language is ambiguous ",
                    "description": " The renewal mechanism is not clearly defined. ",
                    "recommendation": " Clarify whether renewal is automatic or manual. ",
                    "impacted_clause_id": "clause_1",
                }
            ]
        }
    )
    service = RiskAssessmentService(openai_client=client)
    clauses = [
        Clause(
            clause_id="clause_1",
            heading="Term",
            category="term",
            extracted_text="The agreement renews every 12 months unless terminated.",
            confidence=0.9,
            page_reference=2,
        )
    ]

    result = service.analyze("Agreement text", clauses)

    assert client.calls == [
        (
            "Agreement text",
            [
                {
                    "clause_id": "clause_1",
                    "heading": "Term",
                    "category": "term",
                    "extracted_text": "The agreement renews every 12 months unless terminated.",
                }
            ],
        )
    ]
    assert result.risk_flags == [
        RiskFlag(
            risk_id="risk_1",
            severity="medium",
            title="Renewal language is ambiguous",
            description="The renewal mechanism is not clearly defined.",
            recommendation="Clarify whether renewal is automatic or manual.",
            impacted_clause_id="clause_1",
        )
    ]
