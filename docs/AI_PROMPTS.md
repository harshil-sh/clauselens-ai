# AI Prompts

This file defines the intended prompt strategy for the product. The exact prompt text can evolve, but the output contracts should remain stable.

## Principles

- prefer structured JSON output
- keep each prompt focused on one job
- validate and map all outputs in code
- do not rely on the model to invent schema shape
- use consistent category names across prompts

## Prompt 1 — Structured summary

### Goal
Return a concise summary of the document and identify its likely type.

### Expected output
```json
{
  "document_type": "contract",
  "short_summary": "This appears to be a services agreement...",
  "key_points": [
    "12-month term",
    "confidentiality obligations",
    "termination rights are limited"
  ]
}
```

### Prompt draft
```text
You are analysing a business document.

Return valid JSON only.

Tasks:
1. Identify the likely document type
2. Produce a short executive summary
3. Produce 3 to 7 key points

Output schema:
{
  "document_type": "string",
  "short_summary": "string",
  "key_points": ["string"]
}

Document text:
{{document_text}}
```

## Prompt 2 — Clause extraction

### Goal
Extract important clauses into a structured list.

### Suggested categories
- parties
- term
- payment
- confidentiality
- data_protection
- termination
- liability
- indemnity
- intellectual_property
- governing_law
- obligations
- dispute_resolution
- other

### Expected output
```json
{
  "clauses": [
    {
      "heading": "Termination",
      "category": "termination",
      "extracted_text": "Either party may terminate...",
      "confidence": 0.93,
      "page_reference": 4
    }
  ]
}
```

### Prompt draft
```text
You are extracting important clauses from a document.

Return valid JSON only.

Extract the key clauses and classify each clause using one of the allowed categories.

Allowed categories:
parties, term, payment, confidentiality, data_protection, termination, liability, indemnity, intellectual_property, governing_law, obligations, dispute_resolution, other

Output schema:
{
  "clauses": [
    {
      "heading": "string",
      "category": "string",
      "extracted_text": "string",
      "confidence": 0.0,
      "page_reference": 0
    }
  ]
}

Document text:
{{document_text}}
```

## Prompt 3 — Risk assessment

### Goal
Flag meaningful risks based on the document text and extracted clauses.

### Severity scale
- low
- medium
- high

### Expected output
```json
{
  "risk_flags": [
    {
      "severity": "high",
      "title": "No liability cap",
      "description": "The document may expose a party to uncapped liability.",
      "impacted_heading": "Liability",
      "recommendation": "Review and add an explicit liability cap."
    }
  ]
}
```

### Prompt draft
```text
You are reviewing a business document for notable contractual or policy risks.

Return valid JSON only.

Identify concrete risks. Do not invent facts. If a risk is uncertain, describe it cautiously.

Output schema:
{
  "risk_flags": [
    {
      "severity": "low|medium|high",
      "title": "string",
      "description": "string",
      "impacted_heading": "string",
      "recommendation": "string"
    }
  ]
}

Document text:
{{document_text}}

Extracted clauses:
{{clauses_json}}
```

## Implementation note

These prompts should be loaded through a prompt service or prompt file strategy rather than being hardcoded directly inside route handlers.
