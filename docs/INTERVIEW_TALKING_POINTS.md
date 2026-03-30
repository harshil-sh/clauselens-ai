# Interview Talking Points

## Why this project?

ClauseLens AI is a portfolio project built to show applied AI engineering in a workflow that looks like a real product rather than a chatbot demo. Contract and policy analysis is a good fit because it requires file ingestion, normalized parsing, structured AI outputs, persistence, and a usable frontend for review.

## What makes it product-grade?

- typed API contracts between backend and frontend
- explicit service and repository boundaries
- structured AI responses instead of free-form text
- persistence and retrieval instead of single-run output
- error handling, observability, and configuration notes
- a frontend workflow that turns analysis into a usable review experience

## Why did you split the AI work into multiple prompts?

A single prompt can produce impressive demos, but it is harder to validate, debug, and evolve. I split summary, clause extraction, and risk assessment into separate steps so each stage has a narrower contract, clearer failure modes, and better testability.

## Why FastAPI?

FastAPI gives typed request and response models, clean dependency boundaries, and fast iteration for an API-heavy workflow. It is a practical choice for an AI-backed product because it keeps route handlers thin and makes service-layer testing straightforward.

## Why React?

The frontend matters because AI output only becomes useful when it is presented clearly. React and TypeScript let me show full-stack ownership and turn structured backend results into an upload flow, grouped clauses, risk states, and a recent-analyses view that feels like a real product surface.

## How did you manage AI unpredictability?

- structured output schemas
- explicit mapping and validation before returning results
- service boundaries around the OpenAI integration
- mocked tests around analysis contracts
- fallback handling for malformed or partial model responses

## Architecture trade-off summary

### Synchronous analysis vs async jobs

- I kept the MVP synchronous because it reduces infrastructure, makes the local demo simple, and is good enough for smaller documents.
- The trade-off is that larger files and slower model calls will eventually push toward background jobs, status polling, and worker infrastructure.

### SQLite vs Postgres

- SQLite keeps setup friction low and supports a portfolio project that should run quickly on a reviewer machine.
- The trade-off is weaker concurrency and fewer operational guarantees, so the repository boundary preserves a clean path to Postgres later.

### Local uploads vs object storage

- Local file storage is enough for an MVP and keeps the stack cheap and easy to understand.
- The trade-off is that it is not appropriate for multi-instance deployments, so the storage abstraction leaves room for S3-compatible storage.

### Split prompts vs one orchestration prompt

- Split prompts improved reliability, validation, and debugging because each stage has a focused responsibility.
- The trade-off is more orchestration logic and potentially more latency or model cost per document.

### Strict schemas vs flexible free text

- I biased toward strict schemas because persistence, frontend rendering, and tests depend on stable structure.
- The trade-off is that schema design adds upfront effort and can constrain exploratory output, but that is usually the right choice for product workflows.

### Thin routes and services vs quick inline logic

- I kept business logic in services so routes stay simple and side effects are easier to test.
- The trade-off is a bit more structure early, but it avoids a fragile demo architecture once the codebase grows.

## What would you improve next?

- async processing for large files
- auth and user workspaces
- audit trail and version history
- stronger document parsing quality checks
- document comparison mode
- analyst feedback loop for iterative improvement

## Interview-ready summary

If I were summarizing the project in an interview, I would frame it as a low-cost, production-minded AI document analysis system. The main theme is deliberate trade-offs: simple enough to run locally and explain clearly, but structured so it can grow into async processing, stronger storage, and more enterprise-grade workflows without a rewrite.
