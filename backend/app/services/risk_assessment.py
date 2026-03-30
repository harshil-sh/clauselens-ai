from __future__ import annotations

from dataclasses import dataclass

from app.clients.interfaces import ClauseContext, DocumentAnalysisAIClient, RiskAssessmentPayload, RiskFlagPayload
from app.domain.models import Clause, RiskFlag

ALLOWED_RISK_SEVERITIES = {"low", "medium", "high"}


@dataclass(frozen=True)
class RiskAssessmentResult:
    risk_flags: list[RiskFlag]


class RiskMappingError(ValueError):
    pass


class RiskResponseMapper:
    def map(
        self,
        payload: RiskAssessmentPayload,
        *,
        valid_clause_ids: set[str],
    ) -> RiskAssessmentResult:
        risk_flags: list[RiskFlag] = []

        for index, item in enumerate(payload.get("risk_flags", []), start=1):
            risk_flags.append(
                RiskFlag(
                    risk_id=f"risk_{index}",
                    severity=self._normalize_severity(item.get("severity", "")),
                    title=self._normalize_required_text(item, field_name="title"),
                    description=self._normalize_required_text(item, field_name="description"),
                    recommendation=self._normalize_required_text(item, field_name="recommendation"),
                    impacted_clause_id=self._normalize_impacted_clause_id(
                        item.get("impacted_clause_id"),
                        valid_clause_ids=valid_clause_ids,
                    ),
                )
            )

        return RiskAssessmentResult(risk_flags=risk_flags)

    def _normalize_severity(self, value: str) -> str:
        normalized = self._normalize_text(value).lower()
        if normalized not in ALLOWED_RISK_SEVERITIES:
            raise RiskMappingError("Risk response must include severity as low, medium, or high.")
        return normalized

    def _normalize_required_text(self, item: RiskFlagPayload, *, field_name: str) -> str:
        normalized = self._normalize_text(str(item.get(field_name, "")))
        if not normalized:
            raise RiskMappingError(f"Risk response must include {field_name} for each risk flag.")
        return normalized

    def _normalize_impacted_clause_id(
        self,
        value: object,
        *,
        valid_clause_ids: set[str],
    ) -> str | None:
        if value is None:
            return None

        normalized = self._normalize_text(str(value))
        if not normalized or normalized not in valid_clause_ids:
            return None
        return normalized

    def _normalize_text(self, value: str) -> str:
        return " ".join(value.strip().split())


class RiskAssessmentService:
    def __init__(
        self,
        openai_client: DocumentAnalysisAIClient,
        mapper: RiskResponseMapper | None = None,
    ) -> None:
        self._openai_client = openai_client
        self._mapper = mapper or RiskResponseMapper()

    def analyze(self, document_text: str, clauses: list[Clause]) -> RiskAssessmentResult:
        clause_contexts: list[ClauseContext] = [
            {
                "clause_id": clause.clause_id,
                "heading": clause.heading,
                "category": clause.category,
                "extracted_text": clause.extracted_text,
            }
            for clause in clauses
        ]
        payload = self._openai_client.assess_risks(document_text, clause_contexts)
        return self._mapper.map(
            payload,
            valid_clause_ids={clause.clause_id for clause in clauses},
        )
