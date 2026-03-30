from app.api.deps import (
    get_analysis_repository,
    get_document_repository,
    get_openai_client,
    get_prompt_loader,
)
from app.clients.openai import OpenAIDocumentAnalysisAIClient
from app.core.config import clear_settings_cache
from app.domain.models import AnalysisResult, AnalysisSummary, DocumentRecord
from app.repositories.interfaces import AnalysisRepository, DocumentRepository
from app.services.document_analysis import DocumentAnalysisService
from app.services.prompt_loader import FilePromptLoader


def test_document_repository_boundary_uses_in_memory_implementation() -> None:
    repository = get_document_repository()

    saved = repository.save(
        DocumentRecord(
            document_id="doc_123",
            filename="contract.pdf",
            content_type="application/pdf",
        )
    )

    assert isinstance(repository, DocumentRepository)
    assert saved.document_id == "doc_123"
    assert repository.get_by_id("doc_123") == saved


def test_analysis_repository_boundary_uses_in_memory_implementation() -> None:
    repository = get_analysis_repository()
    result = AnalysisResult(
        document_id="doc_456",
        filename="contract.txt",
        document_type="contract",
        summary=AnalysisSummary(short_summary="Summary"),
    )

    saved = repository.save(result)

    assert isinstance(repository, AnalysisRepository)
    assert saved.document_id == "doc_456"
    assert repository.get_by_id("doc_456") == saved
    assert repository.list_recent()[0] == saved


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
