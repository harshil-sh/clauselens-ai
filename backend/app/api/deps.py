from functools import lru_cache

from app.clients.openai import build_openai_client
from app.clients.interfaces import DocumentAnalysisAIClient
from app.clients.mock import MockDocumentAnalysisAIClient
from app.core.config import get_settings
from app.repositories.interfaces import AnalysisRepository, DocumentRepository
from app.repositories.sqlite import (
    SQLiteAnalysisRepository,
    SQLiteDatabase,
    SQLiteDocumentRepository,
)
from app.services.document_analysis import DocumentAnalysisService
from app.services.file_validation import FileValidationService
from app.services.prompt_loader import FilePromptLoader, PromptLoader
from app.services.text_extraction import UploadedDocumentTextExtractionService
from app.services.upload_storage import LocalUploadStorageService


@lru_cache
def get_sqlite_database() -> SQLiteDatabase:
    return SQLiteDatabase(get_settings().sqlite_db_path)


@lru_cache
def get_document_repository() -> DocumentRepository:
    return SQLiteDocumentRepository(get_sqlite_database())


@lru_cache
def get_analysis_repository() -> AnalysisRepository:
    return SQLiteAnalysisRepository(get_sqlite_database())


@lru_cache
def get_openai_client() -> DocumentAnalysisAIClient:
    settings = get_settings()
    if not settings.openai_api_key:
        return MockDocumentAnalysisAIClient()
    return build_openai_client(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        prompt_loader=get_prompt_loader(),
    )


@lru_cache
def get_prompt_loader() -> PromptLoader:
    return FilePromptLoader()


@lru_cache
def get_document_analysis_service() -> DocumentAnalysisService:
    return DocumentAnalysisService(
        repository=get_analysis_repository(),
        openai_client=get_openai_client(),
    )


@lru_cache
def get_file_validation_service() -> FileValidationService:
    return FileValidationService(settings=get_settings())


@lru_cache
def get_local_upload_storage_service() -> LocalUploadStorageService:
    return LocalUploadStorageService(
        settings=get_settings(),
        repository=get_document_repository(),
    )


@lru_cache
def get_uploaded_document_text_extraction_service() -> UploadedDocumentTextExtractionService:
    return UploadedDocumentTextExtractionService()
