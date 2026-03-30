from app.api.deps import (
    get_analysis_repository,
    get_document_repository,
    get_openai_client,
    get_prompt_loader,
    get_request_rate_limiter,
    get_sqlite_database,
)
from app.clients.openai import OpenAIDocumentAnalysisAIClient
from app.core.config import clear_settings_cache
from app.domain.models import AnalysisResult, AnalysisSummary, DocumentRecord
from app.repositories.interfaces import AnalysisRepository, DocumentRepository
from app.repositories.sqlite import SQLiteAnalysisRepository, SQLiteDatabase, SQLiteDocumentRepository
from app.services.document_analysis import DocumentAnalysisService
from app.services.prompt_loader import FilePromptLoader
from app.services.rate_limiting import NoOpRequestRateLimiter, RequestRateLimiter


def test_document_repository_boundary_uses_sqlite_implementation(
    monkeypatch,
    tmp_path,
) -> None:
    from app.api import deps

    db_path = tmp_path / "boundaries.db"
    clear_settings_cache()
    deps.get_sqlite_database.cache_clear()
    deps.get_document_repository.cache_clear()
    monkeypatch.setenv("SQLITE_DB_PATH", str(db_path))

    repository = get_document_repository()

    saved = repository.save(
        DocumentRecord(
            document_id="doc_123",
            filename="contract.pdf",
            content_type="application/pdf",
        )
    )

    assert isinstance(repository, DocumentRepository)
    assert isinstance(repository, SQLiteDocumentRepository)
    assert saved.document_id == "doc_123"
    assert repository.get_by_id("doc_123") == saved

    clear_settings_cache()
    deps.get_sqlite_database.cache_clear()
    deps.get_document_repository.cache_clear()


def test_analysis_repository_boundary_uses_sqlite_implementation(
    monkeypatch,
    tmp_path,
) -> None:
    from app.api import deps

    db_path = tmp_path / "boundaries.db"
    clear_settings_cache()
    deps.get_sqlite_database.cache_clear()
    deps.get_analysis_repository.cache_clear()
    monkeypatch.setenv("SQLITE_DB_PATH", str(db_path))

    repository = get_analysis_repository()
    result = AnalysisResult(
        document_id="doc_456",
        filename="contract.txt",
        document_type="contract",
        summary=AnalysisSummary(short_summary="Summary"),
    )

    saved = repository.save(result)

    assert isinstance(repository, AnalysisRepository)
    assert isinstance(repository, SQLiteAnalysisRepository)
    assert saved.document_id == "doc_456"
    assert repository.get_by_id("doc_456") == saved
    assert repository.list_recent()[0] == saved

    clear_settings_cache()
    deps.get_sqlite_database.cache_clear()
    deps.get_analysis_repository.cache_clear()


def test_sqlite_database_boundary_uses_configured_path(monkeypatch, tmp_path) -> None:
    from app.api import deps

    db_path = tmp_path / "configured.db"
    clear_settings_cache()
    deps.get_sqlite_database.cache_clear()
    monkeypatch.setenv("SQLITE_DB_PATH", str(db_path))

    database = get_sqlite_database()

    assert isinstance(database, SQLiteDatabase)
    assert db_path.exists()

    clear_settings_cache()
    deps.get_sqlite_database.cache_clear()


def test_document_analysis_service_depends_on_ai_boundary() -> None:
    service = DocumentAnalysisService(
        repository=get_analysis_repository(),
        openai_client=get_openai_client(),
    )

    result = service.analyse(
        filename="sample.txt",
        document_text="Sample contract content for testing.",
    )

    assert result.document_type == "contract"
    assert result.summary.short_summary
    assert len(result.clauses) == 1
    assert len(result.risk_flags) == 1


def test_prompt_loader_boundary_uses_file_loader() -> None:
    loader = get_prompt_loader()

    assert isinstance(loader, FilePromptLoader)


def test_openai_boundary_uses_sdk_client_when_api_key_present(monkeypatch) -> None:
    from app.api import deps

    clear_settings_cache()
    deps.get_openai_client.cache_clear()
    deps.get_prompt_loader.cache_clear()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")

    client = get_openai_client()

    assert isinstance(client, OpenAIDocumentAnalysisAIClient)

    clear_settings_cache()
    deps.get_openai_client.cache_clear()
    deps.get_prompt_loader.cache_clear()


def test_rate_limiter_boundary_uses_no_op_strategy() -> None:
    from app.api import deps

    clear_settings_cache()
    deps.get_request_rate_limiter.cache_clear()

    limiter = get_request_rate_limiter()

    assert isinstance(limiter, RequestRateLimiter)
    assert isinstance(limiter, NoOpRequestRateLimiter)

    clear_settings_cache()
    deps.get_request_rate_limiter.cache_clear()
