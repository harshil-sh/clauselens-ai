# Interview Talking Points

## Why this project?

I wanted a portfolio project that demonstrated applied AI engineering in a realistic business workflow. Contract and policy analysis are strong use cases because they involve structured outputs, risk interpretation, and real product design.

## What makes it product-grade?

- typed API contracts
- separated service boundaries
- structured AI responses
- frontend workflow instead of raw backend output
- persistence strategy
- testing approach
- deployment and observability considerations

## Why did you split the AI work into multiple prompts?

A single large prompt is harder to validate and debug. Splitting summary, clause extraction, and risk assessment improves maintainability, testing, and response quality.

## Why FastAPI?

FastAPI gives a clean developer experience, strong typing, and fast iteration for AI-backed APIs.

## Why React?

I wanted to demonstrate full-stack ownership and show how AI output becomes a usable product, not just a backend proof-of-concept.

## How did you manage AI unpredictability?

- structured output schemas
- explicit mapping and validation
- service boundaries around OpenAI
- mocked tests
- fallback handling for malformed responses

## What would you improve next?

- async processing for large files
- auth and user workspaces
- audit trail
- better document parsing quality
- document comparison mode
- analyst feedback loop

## Senior-level trade-off discussions

- synchronous vs async analysis
- local-first MVP vs cloud-first architecture
- SQLite vs Postgres
- raw prompt strings vs prompt management layer
- low-cost build strategy vs enterprise-ready design
