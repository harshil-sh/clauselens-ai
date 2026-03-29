from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyse_document_returns_structured_response() -> None:
    response = client.post(
        "/api/v1/documents/analyse",
        files={"file": ("sample.txt", b"Sample contract content for testing.", "text/plain")},
    )
    assert response.status_code == 200
    body = response.json()
    assert "document_id" in body
    assert body["summary"]["short_summary"]
    assert isinstance(body["clauses"], list)
    assert isinstance(body["risk_flags"], list)


def test_list_recent_analyses() -> None:
    client.post(
        "/api/v1/documents/analyse",
        files={"file": ("sample.txt", b"Another sample contract.", "text/plain")},
    )
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert isinstance(body["items"], list)
