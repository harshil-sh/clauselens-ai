from app.domain.models import AnalysisResult, DocumentRecord
from app.repositories.interfaces import AnalysisRepository, DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    def __init__(self) -> None:
        self._store: dict[str, DocumentRecord] = {}

    def save(self, document: DocumentRecord) -> DocumentRecord:
        self._store[document.document_id] = document
        return document

    def get_by_id(self, document_id: str) -> DocumentRecord | None:
        return self._store.get(document_id)


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
