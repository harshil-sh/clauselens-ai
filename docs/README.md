# ClauseLens AI

ClauseLens AI is a product-grade AI document analyser for contracts and policy documents. A user uploads a document and receives a structured summary, clause extraction, and risk flags through a Python FastAPI backend and React frontend.

This project is designed to demonstrate senior-level credibility in:
- Python backend engineering
- AI integration with OpenAI
- product architecture and delivery
- React frontend implementation
- testability and developer workflow automation

## What the product does

A user can:
1. Upload a contract, policy, or similar text-heavy document
2. Receive a structured executive summary
3. View extracted clauses grouped by category
4. Review risk flags with severity and rationale
5. Download structured JSON output
6. Re-open previous analyses

## Why this is a strong portfolio project

This is not a toy chatbot. It demonstrates:
- real business workflow design
- structured AI outputs instead of plain chat text
- file ingestion and document parsing
- full-stack implementation
- production-minded separation of concerns
- automated development workflow using Codex

## Core capabilities

### MVP
- file upload for PDF, DOCX, and TXT
- text extraction and normalization
- AI-generated structured summary
- clause extraction into categories
- risk flagging with severity
- React results view
- JSON export
- health and retrieval endpoints
- tests for core flows

### Later upgrades
- background jobs for large files
- persistent object storage
- auth and user workspaces
- document comparison
- review workflow and analyst notes

## Recommended stack

### Backend
- Python 3.11
- FastAPI
- Pydantic v2
- Uvicorn
- OpenAI Python SDK
- pytest
- httpx
- SQLite for MVP

### Frontend
- React
- TypeScript
- Vite
- TanStack Query
- React Hook Form
- Zod
- Tailwind CSS
- Vitest + Testing Library

## Suggested repository structure

```text
clauselens-ai/
  backend/
    app/
      api/
      core/
      domain/
      repositories/
      schemas/
      services/
      workers/
      main.py
    tests/
    requirements.txt
    .env.example
  frontend/
    src/
      api/
      components/
      features/
      hooks/
      pages/
      routes/
      types/
      test/
      main.tsx
    package.json
  docs/
    README.md
    ARCHITECTURE.md
    TASKS.md
    AGENTS.md
    API_SPEC.md
    FRONTEND_SPEC.md
    TESTING.md
    DEPLOYMENT.md
    AI_PROMPTS.md
    INTERVIEW_TALKING_POINTS.md
    DECISIONS.md
  tools/
    codex_portfolio_runner.py
    tasks.json
    verify_prompt.txt
```

## Local development

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Demo story for recruiters

“ClauseLens AI is a document intelligence product that analyses contracts and policies using a structured AI pipeline. I designed it to show how I build production-minded AI applications end-to-end: ingestion, extraction, orchestration, typed APIs, frontend UX, and testing.”

## Development approach

This repository is intended to be built incrementally using Codex:
- one task at a time
- verify before moving on
- commit only task-relevant changes
- keep scope narrow and production-minded
