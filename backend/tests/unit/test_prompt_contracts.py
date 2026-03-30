import json
from types import SimpleNamespace

from app.clients.openai import (
    ClauseExtractionResponseModel,
    OpenAIDocumentAnalysisAIClient,
    RiskAssessmentResponseModel,
    SummaryResponseModel,
)
from app.domain.models import Clause, RiskFlag
from app.services.clause_extraction import ClauseExtractionService
from app.services.prompt_loader import PromptLoader, PromptTemplate
from app.services.risk_assessment import RiskAssessmentService
from app.services.summary_analysis import SummaryAnalysisService


class RecordingPromptLoader(PromptLoader):
    def __init__(self) -> None:
        self.calls: list[tuple[PromptTemplate, dict[str, str]]] = []

    def load(self, template: PromptTemplate) -> str:
        return template.value

    def render(self, template: PromptTemplate, **context: str) -> str:
        self.calls.append((template, context))
        return f"{template.value}::{context}"


class FakeParseClient:
    def __init__(self, parsed_models: list[object]) -> None:
        self._parsed_models = list(parsed_models)
        self.calls: list[dict[str, object]] = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        parsed_model = self._parsed_models.pop(0)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(parsed=parsed_model),
                )
            ]
        )


def build_openai_analysis_client(
    *,
    parsed_models: list[object],
    prompt_loader: RecordingPromptLoader,
) -> tuple[OpenAIDocumentAnalysisAIClient, FakeParseClient]:
    parse_client = FakeParseClient(parsed_models=parsed_models)
    sdk_client = SimpleNamespace(
        beta=SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(parse=parse_client.parse),
            )
        )
    )
    return (
        OpenAIDocumentAnalysisAIClient(
            client=sdk_client,
            model="gpt-4.1-mini",
            prompt_loader=prompt_loader,
        ),
        parse_client,
    )


def test_summary_prompt_contract_uses_structured_response_and_maps_result() -> None:
    prompt_loader = RecordingPromptLoader()
    openai_client, parse_client = build_openai_analysis_client(
        parsed_models=[
            SummaryResponseModel(
                document_type=" Service Agreement ",
                short_summary="  Support services are provided under a one-year term. ",
                key_points=[" 12-month term ", " 12-month term ", "Confidentiality obligations"],
            )
        ],
        prompt_loader=prompt_loader,
    )
    service = SummaryAnalysisService(openai_client=openai_client)

    result = service.analyze("Agreement text")

    assert result.document_type == "service_agreement"
    assert result.summary.short_summary == "Support services are provided under a one-year term."
    assert result.summary.key_points == ["12-month term", "Confidentiality obligations"]
    assert prompt_loader.calls == [
        (
            PromptTemplate.SUMMARY_V1,
            {"document_text": "Agreement text"},
        )
    ]
    assert parse_client.calls[0]["response_format"] is SummaryResponseModel
    assert parse_client.calls[0]["messages"] == [
        {
            "role": "user",
            "content": "summary_v1::{'document_text': 'Agreement text'}",
        }
    ]


def test_clause_prompt_contract_uses_structured_response_and_maps_result() -> None:
    prompt_loader = RecordingPromptLoader()
    openai_client, parse_client = build_openai_analysis_client(
        parsed_models=[
            ClauseExtractionResponseModel(
                clauses=[
                    {
                        "heading": " ",
                        "category": "Data Protection",
                        "extracted_text": " Provider must encrypt personal data at rest. ",
                        "confidence": 1.3,
                        "page_reference": 0,
                    }
                ]
            )
        ],
        prompt_loader=prompt_loader,
    )
    service = ClauseExtractionService(openai_client=openai_client)

    result = service.analyze("Agreement text")

    assert result.clauses == [
        Clause(
            clause_id="clause_1",
            heading="Data Protection",
            category="data_protection",
            extracted_text="Provider must encrypt personal data at rest.",
            confidence=1.0,
            page_reference=None,
        )
    ]
    assert prompt_loader.calls == [
        (
            PromptTemplate.CLAUSE_EXTRACTION_V1,
            {"document_text": "Agreement text"},
        )
    ]
    assert parse_client.calls[0]["response_format"] is ClauseExtractionResponseModel
    assert parse_client.calls[0]["messages"] == [
        {
            "role": "user",
            "content": "clause_extraction_v1::{'document_text': 'Agreement text'}",
        }
    ]


def test_risk_prompt_contract_uses_clause_context_and_maps_result() -> None:
    prompt_loader = RecordingPromptLoader()
    openai_client, parse_client = build_openai_analysis_client(
        parsed_models=[
            RiskAssessmentResponseModel(
                risk_flags=[
                    {
                        "severity": " High ",
                        "title": " No liability cap ",
                        "description": " The clause does not cap liability exposure. ",
                        "recommendation": " Add a mutual liability cap. ",
                        "impacted_clause_id": "clause_1",
                    }
                ]
            )
        ],
        prompt_loader=prompt_loader,
    )
    service = RiskAssessmentService(openai_client=openai_client)
    clauses = [
        Clause(
            clause_id="clause_1",
            heading="Liability",
            category="liability",
            extracted_text="Supplier liability is unlimited.",
            confidence=0.91,
            page_reference=2,
        )
    ]

    result = service.analyze("Agreement text", clauses)

    assert result.risk_flags == [
        RiskFlag(
            risk_id="risk_1",
            severity="high",
            title="No liability cap",
            description="The clause does not cap liability exposure.",
            recommendation="Add a mutual liability cap.",
            impacted_clause_id="clause_1",
        )
    ]
    assert prompt_loader.calls == [
        (
            PromptTemplate.RISK_ASSESSMENT_V1,
            {
                "document_text": "Agreement text",
                "clauses_json": json.dumps(
                    [
                        {
                            "clause_id": "clause_1",
                            "heading": "Liability",
                            "category": "liability",
                            "extracted_text": "Supplier liability is unlimited.",
                        }
                    ],
                    indent=2,
                ),
            },
        )
    ]
    assert parse_client.calls[0]["response_format"] is RiskAssessmentResponseModel
    assert parse_client.calls[0]["messages"] == [
        {
            "role": "user",
            "content": "risk_assessment_v1::{'document_text': 'Agreement text', 'clauses_json': '[\\n  {\\n    \"clause_id\": \"clause_1\",\\n    \"heading\": \"Liability\",\\n    \"category\": \"liability\",\\n    \"extracted_text\": \"Supplier liability is unlimited.\"\\n  }\\n]'}",
        }
    ]
