# Architecture

## Overview

ClauseLens AI follows a pipeline-oriented architecture:

1. document upload
2. validation
3. text extraction
4. normalization
5. AI summarization
6. clause extraction
7. risk assessment
8. persistence
9. frontend presentation

The goal is to separate concerns cleanly so the project feels like a real product rather than a thin demo.

## Design principles

- thin API layer
- domain and service boundaries
- structured AI outputs
- explicit contracts
- low-cost MVP infrastructure
- easy local development
- clear upgrade path

## High-level flow

```text
React Frontend
   ->
FastAPI endpoint
   ->
file validation
   ->
document storage
   ->
text extraction
   ->
normalized document model
   ->
OpenAI-backed analysis services
   ->
structured response mapping
   ->
result persistence
   ->
frontend rendering
```

## Backend modules

### `app/api`
Route handlers, dependency wiring, and response mapping.

### `app/core`
Settings, logging, error handling, DI helpers, shared utilities.

### `app/domain`
Core business entities:
- `Document`
- `ExtractedDocument`
- `Clause`
- `RiskFlag`
- `AnalysisResult`

### `app/schemas`
Pydantic request/response models used at API boundaries.

### `app/services`
Business logic:
- `FileValidationService`
- `TextExtractionService`
- `DocumentNormalizationService`
- `SummaryService`
- `ClauseExtractionService`
- `RiskAssessmentService`
- `DocumentAnalysisService`

### `app/repositories`
Persistence interfaces and implementations:
- `DocumentRepository`
- `AnalysisRepository`

### `app/workers`
Reserved for future async processing or job orchestration.

## Frontend design

The frontend should be intentionally product-like rather than decorative.

### Main screens
- upload page
- analysis results page
- recent analyses page

### Main component groups
- upload form
- summary card
- clause list or table
- risk flag list
- empty and error states

### State strategy
- TanStack Query for API requests
- local state for file handling
- typed API contracts shared conceptually with backend response models

## AI orchestration strategy

The AI layer should be structured, not a single giant prompt.

### Step 1: summary
Return:
- document type guess
- short summary
- key points

### Step 2: clause extraction
Return a structured list of clauses:
- heading
- category
- extracted text
- optional page reference
- confidence

### Step 3: risk assessment
Return:
- severity
- title
- description
- linked clause if possible
- recommendation

This separation improves:
- testability
- readability
- prompt maintainability
- failure isolation

## Persistence strategy

### MVP
- local files for uploads
- SQLite for metadata and analysis records

### Upgrade path
- Postgres
- S3-compatible storage
- async job queue
- audit history

## Error handling strategy

Return consistent API error payloads for:
- unsupported file types
- file too large
- extraction failure
- AI response failure
- persistence failure

## Observability goals

Even for a portfolio project, basic operational signals matter:
- request id / correlation id
- structured logs
- duration logging
- failure context without leaking sensitive document content

## Why this architecture is interview-worthy

It gives you a good discussion on:
- separation of concerns
- AI system reliability
- local-first MVP trade-offs
- synchronous vs async design
- storage abstraction
- product growth path
