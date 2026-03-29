# Architecture Decisions

## ADR-001: Use FastAPI for backend
Chosen for typed APIs, clean structure, and fast iteration.

## ADR-002: Use React + TypeScript for frontend
Chosen to demonstrate strong frontend engineering and typed contracts.

## ADR-003: Use SQLite for MVP persistence
Chosen to reduce setup friction and cost while preserving a clean upgrade path.

## ADR-004: Use local file storage for MVP uploads
Chosen to keep the project low-cost and easy to run locally.

## ADR-005: Hide OpenAI behind a dedicated client/service boundary
Chosen so AI integration stays isolated from business logic and route handlers.

## ADR-006: Use structured outputs instead of free-form analysis
Chosen to make persistence, frontend rendering, and testing more reliable.

## ADR-007: Separate summary, clause extraction, and risk prompts
Chosen to improve maintainability, clarity, and error isolation.

## ADR-008: No authentication in MVP
Chosen to focus effort on the core product value rather than account management.
