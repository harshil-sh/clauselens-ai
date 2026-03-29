from app.domain.models import AnalysisResult
from app.repositories.interfaces import AnalysisRepository


class InMemoryAnalysisRepository(AnalysisRepository):
    def __init__(self) -> None:
        self._store: dict[str, AnalysisResult] = {}

    def save(self, result: AnalysisResult) -> AnalysisResult:
        self._store[result.document_id] = result
        return result

    def get_by_id(self, document_id: str) -> AnalysisResult | None:
        return self._store.get(document_id)

    def list_recent(self) -> list[AnalysisResult]:
        return sorted(
            self._store.values(),
            key=lambda item: item.created_at,
            reverse=True,
        )
