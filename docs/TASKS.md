# TASKS

> Rule for Codex: complete exactly one task at a time. Do not start any later task until the current task is finished and verified.

This plan combines:
- **A**: backend starter and production-grade backend architecture
- **B**: frontend starter and recruiter-impressive product UI
- **C**: OpenAI prompts for clause extraction, risk detection, and structured outputs

## Phase 1 — Repository and foundation

- [ ] Task 1: Create production-grade backend folder structure
- [x] Task 2: Set up FastAPI application entrypoint and `/health` endpoint
- [ ] Task 3: Add environment-based settings and configuration management
- [ ] Task 4: Add structured logging and global exception handling
- [x] Task 5: Create repository interfaces and AI client dependency boundaries
- [x] Task 6: Create React + TypeScript frontend skeleton
- [ ] Task 7: Add frontend routing, app shell, and shared UI primitives
- [x] Task 8: Add root-level setup guidance and developer scripts documentation

## Phase 2 — Backend ingestion and parsing

- [ ] Task 9: Implement upload endpoint with file type and size validation
- [ ] Task 10: Add local upload storage strategy for MVP
- [ ] Task 11: Implement TXT text extraction service
- [ ] Task 12: Implement PDF text extraction service
- [ ] Task 13: Implement DOCX text extraction service
- [ ] Task 14: Add normalized extracted document contract
- [ ] Task 15: Add backend tests for validation and extraction flows

## Phase 3 — AI prompt contracts and analysis services

- [ ] Task 16: Add typed OpenAI client wrapper and prompt-loading strategy
- [ ] Task 17: Implement structured summary prompt and mapping logic
- [ ] Task 18: Implement clause extraction prompt and mapping logic
- [ ] Task 19: Implement risk assessment prompt and mapping logic
- [ ] Task 20: Add prompt contract tests using mocked OpenAI responses
- [ ] Task 21: Implement orchestration service for full document analysis
- [ ] Task 22: Expose `POST /api/v1/documents/analyse` returning structured output
- [ ] Task 23: Add fallback handling for malformed or partial AI responses

## Phase 4 — Persistence and retrieval

- [ ] Task 24: Add SQLite models and repositories for documents and analyses
- [x] Task 25: Persist successful analysis results
- [ ] Task 26: Add endpoint to retrieve analysis by document id
- [x] Task 27: Add endpoint to list recent analyses
- [ ] Task 28: Add integration tests for persistence and retrieval flows

## Phase 5 — Frontend analyser experience

- [ ] Task 29: Build upload page with validation and API integration
- [ ] Task 30: Build polished results page with executive summary section
- [ ] Task 31: Render extracted clauses grouped by category
- [ ] Task 32: Render risk flags with severity badges and recommendations
- [ ] Task 33: Add loading, error, and empty states
- [ ] Task 34: Add JSON download action for structured analysis result
- [ ] Task 35: Add recent analyses page
- [ ] Task 36: Add frontend tests for upload, result rendering, and error states

## Phase 6 — Hardening and portfolio polish

- [ ] Task 37: Add API contract documentation with example payloads
- [ ] Task 38: Add CORS, upload size limits, and secure file handling safeguards
- [ ] Task 39: Add request correlation ids and observability notes
- [ ] Task 40: Add rate limiting placeholder or strategy boundary
- [ ] Task 41: Improve automated test coverage across backend and frontend
- [ ] Task 42: Add Dockerfiles for backend and frontend
- [x] Task 43: Final README polish with screenshots placeholders and demo flow
- [ ] Task 44: Add interview talking points and architecture trade-off summary
