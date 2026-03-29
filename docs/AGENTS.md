# AGENTS

This repository is intended to be developed with Codex acting as the implementation agent and the human developer acting as reviewer, architect, and final decision-maker.

## Working model

- Codex must read this file and `docs/TASKS.md` before making changes.
- Codex must work on only one task at a time.
- Codex must not begin later tasks.
- Codex must keep changes minimal, production-minded, and testable.
- Codex must run relevant verification before declaring a task complete.

## Engineering standards

### Backend
- Use Python 3.11.
- Use FastAPI and Pydantic v2.
- Keep route handlers thin.
- Put business logic in services.
- Hide OpenAI and storage details behind boundaries.
- Use explicit request and response models.

### Frontend
- Use React + TypeScript.
- Keep components small and reusable.
- Separate API code from UI components.
- Prefer readable UX with strong empty, loading, and error states.

### AI layer
- Prefer structured outputs over free text.
- Keep prompts versionable and explicit.
- Separate summary, clause extraction, and risk detection concerns.
- Add mapping and validation around AI responses.

### Testing
- Add tests for every meaningful logic change.
- Mock OpenAI and persistence where practical.
- Avoid hidden failures.
- Document known limitations honestly.

## Constraints

- No authentication for MVP.
- SQLite and local file storage are acceptable.
- Avoid unnecessary overengineering.
- Preserve a clear upgrade path for async processing and stronger infra later.

## Required final response format for each Codex task

1. Plan
2. Changes made
3. Files updated
4. Verification performed
5. Whether the task is fully complete

## Commit guidance

When a task is complete and verified, use commit messages like:

```text
feat(task-18): implement clause extraction prompt and mapping logic
```

## What success looks like

A reviewer should be able to:
- understand the architecture quickly
- run the app locally
- see clear product value
- inspect tests and trust the structure
- discuss trade-offs in an interview
