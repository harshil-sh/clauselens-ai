import time
from pathlib import Path

from app.clients.mock import MockDocumentAnalysisAIClient
from app.repositories.sqlite import SQLiteAnalysisRepository, SQLiteDatabase
from app.services.document_analysis import DocumentAnalysisService


def _build_service(db_path: Path) -> DocumentAnalysisService:
    repository = SQLiteAnalysisRepository(SQLiteDatabase(str(db_path)))
    return DocumentAnalysisService(
        repository=repository,
        openai_client=MockDocumentAnalysisAIClient(),
    )


def test_analysis_result_persists_and_can_be_retrieved_from_a_fresh_service(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "clauselens.db"

    created = _build_service(db_path).analyse(
        filename="retrieval.txt",
        document_text="Contract content for retrieval.",
    )
    fetched = _build_service(db_path).get_by_id(created.document_id)

    assert db_path.exists()
    assert fetched == created


def test_retrieval_returns_none_for_unknown_document_id(tmp_path: Path) -> None:
    db_path = tmp_path / "clauselens.db"

    fetched = _build_service(db_path).get_by_id("doc_missing")

    assert fetched is None


def test_list_recent_returns_persisted_items_in_descending_created_order(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "clauselens.db"
    service = _build_service(db_path)

    first = service.analyse(
        filename="first.txt",
        document_text="First contract sample.",
    )
    time.sleep(1.1)
    second = service.analyse(
        filename="second.txt",
        document_text="Second contract sample.",
    )

    recent = _build_service(db_path).list_recent()

    assert [item.document_id for item in recent] == [
        second.document_id,
        first.document_id,
    ]
    assert recent[0] == second
    assert recent[1] == first
