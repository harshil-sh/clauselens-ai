from app.main import app


def test_openapi_includes_document_examples_and_error_contracts() -> None:
    schema = app.openapi()
    paths = schema["paths"]

    upload_post = paths["/api/v1/documents/upload"]["post"]
    analyse_post = paths["/api/v1/documents/analyse"]["post"]
    get_analysis = paths["/api/v1/documents/{document_id}"]["get"]
    list_analyses = paths["/api/v1/documents"]["get"]

    upload_example = upload_post["responses"]["200"]["content"]["application/json"]["example"]
    analyse_example = analyse_post["responses"]["200"]["content"]["application/json"]["example"]
    list_example = list_analyses["responses"]["200"]["content"]["application/json"]["example"]
    not_found_example = get_analysis["responses"]["404"]["content"]["application/json"]["examples"][
        "not_found"
    ]["value"]

    assert upload_example["document_id"] == "doc_123"
    assert upload_example["content_type"] == "application/pdf"

    assert analyse_post["requestBody"]["content"]["multipart/form-data"]["schema"]["required"] == [
        "file"
    ]
    assert analyse_example["summary"]["short_summary"]
    assert analyse_example["clauses"][0]["clause_id"] == "clause_termination"
    assert analyse_example["risk_flags"][0]["risk_id"] == "risk_liability_cap"

    assert get_analysis["responses"]["200"]["content"]["application/json"]["example"] == analyse_example
    assert not_found_example == {
        "error": {
            "code": "not_found",
            "message": "Analysis result was not found.",
        }
    }

    assert list_example["items"][0]["document_id"] == "doc_123"
    assert list_example["items"][1]["document_id"] == "doc_122"
