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


def test_get_document_analysis_by_document_id() -> None:
    create_response = client.post(
        "/api/v1/documents/analyse",
        files={"file": ("retrieval.txt", b"Contract content for retrieval.", "text/plain")},
    )
    document_id = create_response.json()["document_id"]

    response = client.get(f"/api/v1/documents/{document_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["document_id"] == document_id
    assert body["filename"] == "retrieval.txt"
    assert "summary" in body
    assert isinstance(body["clauses"], list)
    assert isinstance(body["risk_flags"], list)


def test_get_document_analysis_returns_not_found_for_unknown_document_id() -> None:
    response = client.get("/api/v1/documents/doc_missing")
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": "Analysis result was not found.",
        }
    }


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
