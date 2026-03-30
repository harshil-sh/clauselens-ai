from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from app.clients.interfaces import ClauseExtractionPayload, DocumentAnalysisAIClient, ExtractedClausePayload
from app.domain.models import Clause

ALLOWED_CLAUSE_CATEGORIES = {
    "parties",
    "term",
    "payment",
    "confidentiality",
    "data_protection",
    "termination",
    "liability",
    "indemnity",
    "intellectual_property",
    "governing_law",
    "obligations",
    "dispute_resolution",
    "other",
}


@dataclass(frozen=True)
class ClauseExtractionResult:
    clauses: list[Clause]


class ClauseMappingError(ValueError):
    pass


class ClauseResponseMapper:
    def map(self, payload: ClauseExtractionPayload) -> ClauseExtractionResult:
        clauses: list[Clause] = []
        last_error: ClauseMappingError | None = None

        for index, item in enumerate(payload.get("clauses", []), start=1):
            try:
                extracted_text = self._normalize_extracted_text(item)
                heading = self._normalize_heading(item, index=index)
                category = self._normalize_category(item.get("category", ""))
                confidence = self._normalize_confidence(item.get("confidence"))
                page_reference = self._normalize_page_reference(item.get("page_reference"))
            except ClauseMappingError as exc:
                last_error = exc
                continue

            clauses.append(
                Clause(
                    clause_id=f"clause_{index}",
                    heading=heading,
                    category=category,
                    extracted_text=extracted_text,
                    confidence=confidence,
                    page_reference=page_reference,
                )
            )

        if payload.get("clauses") and not clauses and last_error is not None:
            raise last_error

        return ClauseExtractionResult(clauses=clauses)

    def _normalize_heading(self, item: ExtractedClausePayload, *, index: int) -> str:
        heading = self._normalize_text(item.get("heading", ""))
        if heading:
            return heading

        category = self._normalize_category(item.get("category", ""))
        if category != "other":
            return category.replace("_", " ").title()

        return f"Clause {index}"

    def _normalize_extracted_text(self, item: ExtractedClausePayload) -> str:
        extracted_text = self._normalize_text(item.get("extracted_text", ""))
        if not extracted_text:
            raise ClauseMappingError("Clause response must include extracted_text for each clause.")
        return extracted_text

    def _normalize_category(self, value: str) -> str:
        normalized = "_".join(self._normalize_text(value).lower().split())
        if not normalized:
            return "other"
        if normalized not in ALLOWED_CLAUSE_CATEGORIES:
            return "other"
        return normalized

    def _normalize_confidence(self, value: object) -> float:
        if value is None:
            return 0.0

        try:
            confidence = float(value)
        except (TypeError, ValueError) as exc:
            raise ClauseMappingError("Clause confidence must be numeric.") from exc

        if confidence < 0:
            return 0.0
        if confidence > 1:
            return 1.0
        return confidence

    def _normalize_page_reference(self, value: object) -> int | None:
        if value is None:
            return None

        try:
            page_reference = int(value)
        except (TypeError, ValueError) as exc:
            raise ClauseMappingError("Clause page_reference must be an integer.") from exc

        if page_reference < 1:
            return None
        return page_reference

    def _normalize_text(self, value: str) -> str:
        return " ".join(value.strip().split())


class ClauseExtractionService:
    def __init__(
        self,
        openai_client: DocumentAnalysisAIClient,
        mapper: ClauseResponseMapper | None = None,
    ) -> None:
        self._openai_client = openai_client
        self._mapper = mapper or ClauseResponseMapper()

    def analyze(self, document_text: str) -> ClauseExtractionResult:
        payload = self._openai_client.extract_clauses(document_text)
        return self._mapper.map(payload)
