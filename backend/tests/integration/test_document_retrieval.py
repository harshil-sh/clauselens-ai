import asyncio
import json
from datetime import datetime

from app.api.deps import get_document_analysis_service
from app.domain.models import AnalysisResult, AnalysisSummary, Clause, RiskFlag
from app.main import app


class StubDocumentAnalysisService:
    def get_by_id(self, document_id: str) -> AnalysisResult | None:
        if document_id != "doc_123":
            return None
        return AnalysisResult(
            document_id="doc_123",
            filename="contract.txt",
            document_type="contract",
            summary=AnalysisSummary(
                short_summary="Short summary",
                key_points=["Point 1", "Point 2"],
            ),
            clauses=[
                Clause(
                    clause_id="clause_1",
                    heading="Termination",
                    category="termination",
                    extracted_text="Either party may terminate for breach.",
                    confidence=0.91,
                    page_reference=2,
                )
            ],
            risk_flags=[
                RiskFlag(
                    risk_id="risk_1",
                    severity="medium",
                    title="Termination rights are narrow",
                    description="The clause allows termination only for breach.",
                    recommendation="Confirm whether convenience termination is needed.",
                    impacted_clause_id="clause_1",
                )
            ],
            created_at=datetime(2026, 3, 30, 10, 0, 0),
        )


def call_app(path: str) -> tuple[int, dict[str, object]]:
    messages: list[dict[str, object]] = []
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    asyncio.run(asyncio.wait_for(app(scope, receive, send), timeout=3))

    response_start = next(
        message for message in messages if message["type"] == "http.response.start"
    )
    response_body = next(
        message for message in messages if message["type"] == "http.response.body"
    )
    return response_start["status"], json.loads(response_body["body"])


def test_get_document_analysis_by_document_id() -> None:
    app.dependency_overrides[get_document_analysis_service] = lambda: StubDocumentAnalysisService()
    try:
        status_code, body = call_app("/api/v1/documents/doc_123")
    finally:
        app.dependency_overrides.clear()

    assert status_code == 200
    assert body["document_id"] == "doc_123"
    assert body["filename"] == "contract.txt"
    assert body["document_type"] == "contract"
    assert body["summary"]["short_summary"] == "Short summary"
    assert body["clauses"][0]["clause_id"] == "clause_1"
    assert body["risk_flags"][0]["impacted_clause_id"] == "clause_1"


def test_get_document_analysis_returns_not_found_for_unknown_document_id() -> None:
    status_code, body = call_app("/api/v1/documents/doc_missing")

    assert status_code == 404
    assert body == {
        "error": {
            "code": "not_found",
            "message": "Analysis result was not found.",
        }
    }
