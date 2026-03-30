# ClauseLens AI

ClauseLens AI is a full-stack document analysis application with a FastAPI backend and a React + TypeScript frontend.

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

## Developer automation

The repository includes [`tools/codex_portfolio_runner.py`](/home/harshil/workspace/clauselens-ai/tools/codex_portfolio_runner.py) for sequential Codex task execution and verification.

Show available options:

```bash
python3 tools/codex_portfolio_runner.py --help
```

## Additional context

See [`docs/README.md`](/home/harshil/workspace/clauselens-ai/docs/README.md) for the broader product and portfolio overview.
