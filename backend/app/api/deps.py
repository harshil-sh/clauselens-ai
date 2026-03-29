from functools import lru_cache

from app.clients.interfaces import DocumentAnalysisAIClient
from app.clients.mock import MockDocumentAnalysisAIClient
from app.repositories.in_memory import InMemoryAnalysisRepository, InMemoryDocumentRepository
from app.repositories.interfaces import AnalysisRepository, DocumentRepository
from app.services.document_analysis import DocumentAnalysisService


@lru_cache
def get_document_repository() -> DocumentRepository:
    return InMemoryDocumentRepository()


@lru_cache
def get_analysis_repository() -> AnalysisRepository:
    return InMemoryAnalysisRepository()


@lru_cache
def get_openai_client() -> DocumentAnalysisAIClient:
    return MockDocumentAnalysisAIClient()


@lru_cache
def get_document_analysis_service() -> DocumentAnalysisService:
    return DocumentAnalysisService(
        repository=get_analysis_repository(),
        openai_client=get_openai_client(),
    )
