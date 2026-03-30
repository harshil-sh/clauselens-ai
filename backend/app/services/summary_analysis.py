from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.clients.interfaces import DocumentAnalysisAIClient, SummaryPayload
from app.domain.models import AnalysisSummary


@dataclass(frozen=True)
class SummaryAnalysisResult:
    document_type: str
    summary: AnalysisSummary


class SummaryMappingError(ValueError):
    pass


class SummaryResponseMapper:
    def map(self, payload: SummaryPayload) -> SummaryAnalysisResult:
        document_type = self._normalize_document_type(payload.get("document_type", ""))
        short_summary = self._normalize_short_summary(payload.get("short_summary", ""))
        key_points = self._normalize_key_points(payload.get("key_points", []))

        return SummaryAnalysisResult(
            document_type=document_type,
            summary=AnalysisSummary(
                short_summary=short_summary,
                key_points=key_points,
            ),
        )

    def _normalize_document_type(self, value: str) -> str:
        normalized = "_".join(value.strip().lower().split())
        return normalized or "unknown"

    def _normalize_short_summary(self, value: str) -> str:
        normalized = " ".join(value.strip().split())
        if not normalized:
            raise SummaryMappingError("Summary response must include a short_summary value.")
        return normalized

    def _normalize_key_points(self, values: Iterable[str]) -> list[str]:
        normalized_points: list[str] = []
        seen: set[str] = set()

        for value in values:
            normalized = " ".join(value.strip().split())
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            normalized_points.append(normalized)
            if len(normalized_points) == 7:
                break

        return normalized_points


class SummaryAnalysisService:
    def __init__(
        self,
        openai_client: DocumentAnalysisAIClient,
        mapper: SummaryResponseMapper | None = None,
    ) -> None:
        self._openai_client = openai_client
        self._mapper = mapper or SummaryResponseMapper()

    def analyze(self, document_text: str) -> SummaryAnalysisResult:
        payload = self._openai_client.summarize(document_text)
        return self._mapper.map(payload)
