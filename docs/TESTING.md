# Testing Strategy

## Goals

Testing should prove that the project is more than a visual demo. It should show reliable engineering decisions.

## Backend tests

### Unit tests
- settings and config
- file validation
- text extraction services
- AI response mapping
- orchestration logic
- repository behavior where practical

### Integration tests
- `GET /health`
- upload endpoint validation
- full analyse flow with mocked AI responses
- retrieval endpoints
- recent analyses listing

## Frontend tests

- upload form validation
- loading state
- error state
- summary rendering
- grouped clauses rendering
- risk severity badges
- recent analyses rendering

## Mocking strategy

- mock OpenAI responses
- avoid external network in tests
- mock file storage where appropriate
- keep fixtures small and explicit

## Suggested commands

### Backend
```bash
pytest
```

### Frontend
```bash
npm test
```

## Quality bar

A task is not complete until:
- the relevant tests pass, or
- the reason they cannot be added yet is clearly documented

## Portfolio angle

Strong tests help you discuss:
- reliability
- maintainability
- AI response validation
- failure handling
- engineering maturity
