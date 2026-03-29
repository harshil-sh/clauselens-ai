from functools import lru_cache

from app.repositories.in_memory import InMemoryAnalysisRepository
from app.repositories.interfaces import AnalysisRepository
from app.services.document_analysis import DocumentAnalysisService
from app.services.openai_client import MockOpenAIClient, OpenAIClient


@lru_cache
def get_analysis_repository() -> AnalysisRepository:
    return InMemoryAnalysisRepository()


@lru_cache
def get_openai_client() -> OpenAIClient:
    return MockOpenAIClient()


@lru_cache
def get_document_analysis_service() -> DocumentAnalysisService:
    return DocumentAnalysisService(
        repository=get_analysis_repository(),
        openai_client=get_openai_client(),
    )
