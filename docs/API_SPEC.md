# API Specification

## Base path

`/api/v1`

## Endpoints

### `GET /health`
Simple health check.

#### Response
```json
{
  "status": "ok"
}
```

---

### `POST /documents/analyse`
Upload and analyse a document.

#### Request
`multipart/form-data`

Fields:
- `file`: required, one file
- supported types: PDF, DOCX, TXT

#### Success response
```json
{
  "document_id": "doc_123",
  "filename": "services-agreement.pdf",
  "document_type": "contract",
  "summary": {
    "short_summary": "This appears to be a services agreement with a 12-month term.",
    "key_points": [
      "12-month initial term",
      "broad confidentiality obligations",
      "liability cap not clearly defined"
    ]
  },
  "clauses": [
    {
      "clause_id": "clause_1",
      "heading": "Termination",
      "category": "termination",
      "extracted_text": "Either party may terminate for material breach...",
      "confidence": 0.94,
      "page_reference": 4
    }
  ],
  "risk_flags": [
    {
      "risk_id": "risk_1",
      "severity": "high",
      "title": "No explicit liability cap",
      "description": "The agreement may expose one party to uncapped liability.",
      "impacted_clause_id": "clause_7",
      "recommendation": "Review liability language and consider adding a cap."
    }
  ],
  "created_at": "2026-03-29T12:00:00Z"
}
```

---

### `GET /documents/{document_id}`
Retrieve one previous analysis result.

---

### `GET /documents`
List recent analyses.

#### Example list response
```json
{
  "items": [
    {
      "document_id": "doc_123",
      "filename": "services-agreement.pdf",
      "document_type": "contract",
      "created_at": "2026-03-29T12:00:00Z"
    }
  ]
}
```

## Error contract

```json
{
  "error": {
    "code": "unsupported_file_type",
    "message": "Only PDF, DOCX, and TXT files are supported."
  }
}
```

## Error examples

### File too large
```json
{
  "error": {
    "code": "file_too_large",
    "message": "The uploaded file exceeds the maximum allowed size."
  }
}
```

### Extraction failure
```json
{
  "error": {
    "code": "extraction_failed",
    "message": "Document text could not be extracted."
  }
}
```

### AI analysis failure
```json
{
  "error": {
    "code": "analysis_failed",
    "message": "Structured document analysis could not be completed."
  }
}
```
