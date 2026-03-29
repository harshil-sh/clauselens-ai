# Frontend Specification

## Product goals

The frontend should feel like a real internal product:
- clean
- professional
- readable
- focused on utility rather than decoration

## User journey

1. User lands on upload screen
2. User selects a document
3. User submits for analysis
4. UI shows progress/loading state
5. UI displays summary, clauses, and risks
6. User downloads JSON or revisits a recent analysis

## Main pages

### Upload page
Contains:
- title and short product description
- supported file types note
- file picker
- submit action
- validation errors

### Analysis results page
Contains:
- document metadata header
- summary card
- extracted clauses grouped by category
- risk flag list
- JSON export action

### Recent analyses page
Contains:
- list of recent uploads
- created timestamp
- document type
- link to result view

## Component suggestions

- `PageShell`
- `FileUploadCard`
- `SummaryCard`
- `KeyPointsList`
- `ClauseGroup`
- `ClauseTable`
- `RiskFlagList`
- `SeverityBadge`
- `ApiErrorBanner`
- `EmptyState`

## State management

- TanStack Query for API interactions
- component state for file selection
- route params for `document_id`
- typed response models in `src/types`

## UX standards

- disable submit while request is running
- show supported file types clearly
- show friendly error messages
- keep hierarchy obvious
- make risk severity visually distinct
- keep content readable on laptop-sized screens

## Testing expectations

Frontend tests should cover:
- file validation
- upload action
- loading state
- error state
- summary rendering
- clause rendering
- risk flag rendering
- JSON download visibility or action trigger
