from datetime import datetime, timedelta

from app.domain.models import AnalysisResult, AnalysisSummary, Clause, DocumentRecord, RiskFlag
from app.repositories.sqlite import SQLiteAnalysisRepository, SQLiteDatabase, SQLiteDocumentRepository


def test_sqlite_document_repository_round_trips_document_record(tmp_path) -> None:
    repository = SQLiteDocumentRepository(SQLiteDatabase(str(tmp_path / "documents.db")))
    created_at = datetime(2026, 3, 30, 10, 15, 0)
    document = DocumentRecord(
        document_id="doc_sqlite_1",
        filename="msa.pdf",
        content_type="application/pdf",
        storage_path="/tmp/msa.pdf",
        created_at=created_at,
    )

    saved = repository.save(document)
    fetched = repository.get_by_id("doc_sqlite_1")

    assert saved == document
    assert fetched == document


def test_sqlite_analysis_repository_round_trips_full_analysis_result(tmp_path) -> None:
    repository = SQLiteAnalysisRepository(SQLiteDatabase(str(tmp_path / "analyses.db")))
    created_at = datetime(2026, 3, 30, 11, 0, 0)
    result = AnalysisResult(
        document_id="doc_sqlite_2",
        filename="terms.txt",
        document_type="service_agreement",
        summary=AnalysisSummary(
            short_summary="Support agreement summary.",
            key_points=["Auto-renewal", "30 day termination"],
        ),
        clauses=[
            Clause(
                clause_id="clause_1",
                heading="Term",
                category="term",
                extracted_text="Initial term is 12 months.",
                confidence=0.91,
                page_reference=2,
            )
        ],
        risk_flags=[
            RiskFlag(
                risk_id="risk_1",
                severity="medium",
                title="Auto-renewal",
                description="Renews automatically.",
                recommendation="Add explicit notice window.",
                impacted_clause_id="clause_1",
            )
        ],
        created_at=created_at,
    )

    saved = repository.save(result)
    fetched = repository.get_by_id("doc_sqlite_2")

    assert saved == result
    assert fetched == result


def test_sqlite_analysis_repository_lists_recent_results_descending(tmp_path) -> None:
    repository = SQLiteAnalysisRepository(SQLiteDatabase(str(tmp_path / "recent.db")))
    older = AnalysisResult(
        document_id="doc_older",
        filename="older.txt",
        document_type="contract",
        summary=AnalysisSummary(short_summary="Older"),
        created_at=datetime(2026, 3, 30, 9, 0, 0),
    )
    newer = AnalysisResult(
        document_id="doc_newer",
        filename="newer.txt",
        document_type="contract",
        summary=AnalysisSummary(short_summary="Newer"),
        created_at=older.created_at + timedelta(hours=1),
    )

    repository.save(older)
    repository.save(newer)

    assert [item.document_id for item in repository.list_recent()] == [
        "doc_newer",
        "doc_older",
    ]
