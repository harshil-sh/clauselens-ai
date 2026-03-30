# Deployment Notes

## MVP deployment strategy

For portfolio purposes, keep deployment practical and low-cost.

### Recommended approach
- Frontend on Vercel or Netlify
- Backend on Render, Railway, Fly.io, or local demo
- SQLite for local demo, Postgres for hosted upgrade
- local file storage for MVP, object storage later

## Local-first recommendation

Before paying for hosting:
- run locally
- produce a short demo video
- ensure UX and outputs look polished
- deploy only after core flow works well

## Environment variables

### Backend
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `APP_ENV`
- `MAX_UPLOAD_MB`
- `DATABASE_URL`

### Frontend
- `VITE_API_BASE_URL`

## Docker plan

Add:
- backend Dockerfile
- frontend Dockerfile
- optional docker-compose for local demo

## Security notes

- validate file size and type
- do not trust filename extension alone
- isolate uploaded files
- avoid logging full document contents
- sanitize error responses

## Observability notes

- accept an incoming `X-Request-ID` header and generate one when absent
- return `X-Request-ID` on every response so client-side errors can be correlated to backend logs
- emit structured request completion logs with path, method, request id, and duration in milliseconds
- include request ids on warning and error logs without logging raw document text
