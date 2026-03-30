# ClauseLens AI

ClauseLens AI is a full-stack document analysis application for contracts and policy documents. It combines a FastAPI backend with a React + TypeScript frontend to turn uploaded files into a structured summary, extracted clauses, and risk flags.

## What it does

ClauseLens AI is designed to demonstrate a production-minded AI workflow instead of a chat-only demo:

- upload a PDF, DOCX, or TXT document
- extract normalized document text
- generate a structured executive summary
- group clauses into readable categories
- highlight risk flags with severity and rationale
- re-open prior analyses and export JSON output

## Demo flow

Use this flow when walking the project through for reviewers or recruiters:

1. Open the upload page and choose a contract or policy file.
2. Submit the document to trigger the backend analysis pipeline.
3. Review the executive summary and top key points on the analysis page.
4. Scroll through clause groups to show structured extraction.
5. Inspect the risk section to explain severity badges and impacted clauses.
6. Download the JSON result and open the recent analyses page to show retrieval.

## Screenshots

Add final product screenshots under `docs/assets/screenshots/` using the placeholder names below, then replace the placeholder text with embedded images.

- `docs/assets/screenshots/upload-page.png`: upload experience
- `docs/assets/screenshots/analysis-summary.png`: executive summary and key metrics
- `docs/assets/screenshots/analysis-risks.png`: clause groups and risk flags
- `docs/assets/screenshots/recent-analyses.png`: history and retrieval flow

Placeholder gallery:

- `[Upload page screenshot placeholder](docs/assets/screenshots/upload-page.png)`
- `[Analysis summary screenshot placeholder](docs/assets/screenshots/analysis-summary.png)`
- `[Analysis risks screenshot placeholder](docs/assets/screenshots/analysis-risks.png)`
- `[Recent analyses screenshot placeholder](docs/assets/screenshots/recent-analyses.png)`

## Repository layout

- `backend/`: FastAPI API, application services, and tests
- `frontend/`: Vite-powered React client
- `docs/`: project planning and architecture notes
- `tools/`: local developer automation utilities

## Prerequisites

- Python 3.11 for backend development
- Node.js 20+ and npm for frontend development

## Quick start

### 1. Set up the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

The backend runs on `http://localhost:8001`.

### 2. Set up the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173`.

By default, the frontend targets `http://localhost:8001/api/v1`. Override that with `VITE_API_BASE_URL` if needed.

### 3. Optional demo seed

After both services are running, upload one of the sample files already stored under `backend/data/uploads/` to exercise the full flow locally.

## Environment configuration

Backend settings are read from `backend/.env` or a root `.env`. Start from [`backend/.env.example`](/home/harshil/workspace/clauselens-ai/backend/.env.example).

Current backend settings include:

- `APP_NAME`
- `APP_ENV`
- `API_V1_PREFIX`
- `OPENAI_MODEL`
- `OPENAI_API_KEY`
- `MAX_UPLOAD_MB`
- `UPLOAD_DIR`
- `ALLOWED_FILE_EXTENSIONS`
- `CORS_ALLOWED_ORIGINS`

## Developer commands

### Backend

Run the API locally:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

Run tests:

```bash
cd backend
source .venv/bin/activate
python3 -m pytest
```

### Frontend scripts

From `frontend/`:

- `npm run dev`: start the Vite development server
- `npm run build`: run TypeScript compilation and create a production build
- `npm run preview`: preview the production build locally
- `npm run typecheck`: run TypeScript type-checking without emitting files

## Architecture snapshot

- `backend/`: FastAPI routes, services, repositories, prompt contracts, and tests
- `frontend/`: upload flow, analysis results, recent analyses, and UI tests
- `docs/`: API, architecture, testing, deployment, and interview notes
- `tools/`: local workflow automation for sequential task execution and verification

## Developer automation

The repository includes [`tools/codex_portfolio_runner.py`](/home/harshil/workspace/clauselens-ai/tools/codex_portfolio_runner.py) for sequential Codex task execution and verification.

Show available options:

```bash
python3 tools/codex_portfolio_runner.py --help
```

## Additional context

See [`docs/README.md`](/home/harshil/workspace/clauselens-ai/docs/README.md) for the broader product and portfolio overview.
See [`docs/INTERVIEW_TALKING_POINTS.md`](/home/harshil/workspace/clauselens-ai/docs/INTERVIEW_TALKING_POINTS.md) for interview-ready talking points and architecture trade-offs.
