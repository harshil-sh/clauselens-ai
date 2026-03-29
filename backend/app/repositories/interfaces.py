from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models import AnalysisResult


class AnalysisRepository(ABC):
    @abstractmethod
    def save(self, result: AnalysisResult) -> AnalysisResult:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, document_id: str) -> AnalysisResult | None:
        raise NotImplementedError

    @abstractmethod
    def list_recent(self) -> list[AnalysisResult]:
        raise NotImplementedError
