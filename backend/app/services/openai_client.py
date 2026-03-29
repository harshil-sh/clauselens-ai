from app.clients.interfaces import DocumentAnalysisAIClient as OpenAIClient
from app.clients.mock import MockDocumentAnalysisAIClient as MockOpenAIClient

__all__ = ["MockOpenAIClient", "OpenAIClient"]
