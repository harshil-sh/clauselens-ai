# API Specification

## Contract source

The canonical API contract is the FastAPI OpenAPI document exposed by the backend:

- `GET /openapi.json`
- `GET /docs`

This document is a concise reference for the currently implemented endpoints and example payloads.

## Base path

- API routes: `/api/v1`
- Health route: `/health`

## Endpoints

### `GET /health`

Basic service readiness check.

Example response:

```json
{
  "status": "ok"
}
```

### `POST /api/v1/documents/upload`

Validates and stores a single uploaded document.

Request:

- Content type: `multipart/form-data`
- Field: `file`
- Supported file types: `PDF`, `DOCX`, `TXT`

Example success response:

```json
{
  "document_id": "doc_123",
  "filename": "services-agreement.pdf",
  "content_type": "application/pdf",
  "size_bytes": 48213
}
```

### `POST /api/v1/documents/analyse`

Validates a single uploaded document, extracts text, and returns structured analysis output.

Request:

- Content type: `multipart/form-data`
- Field: `file`
- Supported file types: `PDF`, `DOCX`, `TXT`

Example success response:

```json
{
  "document_id": "doc_123",
  "filename": "services-agreement.pdf",
  "document_type": "contract",
  "summary": {
    "short_summary": "This appears to be a services agreement with a 12-month initial term.",
    "key_points": [
      "The agreement renews automatically unless notice is given.",
      "Confidentiality obligations continue after termination.",
      "The liability section should be reviewed before signature."
    ]
  },
  "clauses": [
    {
      "clause_id": "clause_termination",
      "heading": "Termination",
      "category": "termination",
      "extracted_text": "Either party may terminate for material breach with 30 days' notice.",
      "confidence": 0.94,
      "page_reference": 4
    }
  ],
  "risk_flags": [
    {
      "risk_id": "risk_liability_cap",
      "severity": "high",
      "title": "Liability cap is missing",
      "description": "The agreement does not define a clear cap on direct damages.",
      "recommendation": "Add a mutual liability cap tied to fees paid under the agreement.",
      "impacted_clause_id": "clause_liability"
    }
  ],
  "created_at": "2026-03-30T10:00:00Z"
}
```

### `GET /api/v1/documents/{document_id}`

Returns a previously saved analysis result by document id.

Example success response:

```json
{
  "document_id": "doc_123",
  "filename": "services-agreement.pdf",
  "document_type": "contract",
  "summary": {
    "short_summary": "This appears to be a services agreement with a 12-month initial term.",
    "key_points": [
      "The agreement renews automatically unless notice is given.",
      "Confidentiality obligations continue after termination.",
      "The liability section should be reviewed before signature."
    ]
  },
  "clauses": [
    {
      "clause_id": "clause_termination",
      "heading": "Termination",
      "category": "termination",
      "extracted_text": "Either party may terminate for material breach with 30 days' notice.",
      "confidence": 0.94,
      "page_reference": 4
    }
  ],
  "risk_flags": [
    {
      "risk_id": "risk_liability_cap",
      "severity": "high",
      "title": "Liability cap is missing",
      "description": "The agreement does not define a clear cap on direct damages.",
      "recommendation": "Add a mutual liability cap tied to fees paid under the agreement.",
      "impacted_clause_id": "clause_liability"
    }
  ],
  "created_at": "2026-03-30T10:00:00Z"
}
```

### `GET /api/v1/documents`

Lists recent saved analyses in descending creation order.

Example success response:

```json
{
  "items": [
    {
      "document_id": "doc_123",
      "filename": "services-agreement.pdf",
      "document_type": "contract",
      "created_at": "2026-03-30T10:00:00Z"
    },
    {
      "document_id": "doc_122",
      "filename": "nda.txt",
      "document_type": "contract",
      "created_at": "2026-03-30T09:45:00Z"
    }
  ]
}
```

## Error contract

Structured errors are returned as:

```json
{
  "error": {
    "code": "not_found",
    "message": "Analysis result was not found."
  }
}
```

Validation failures may also include `details`.

Example validation error:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "details": [
      {
        "type": "missing",
        "loc": ["body", "file"],
        "msg": "Field required",
        "input": null
      }
    ]
  }
}
```
