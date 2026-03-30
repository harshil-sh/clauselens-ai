import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import Settings, get_settings
from app.core.logging import request_id_context
from app.services.rate_limiting import RequestRateLimiter

logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or f"req_{uuid4().hex}"
        request.state.request_id = request_id

        context_token = request_id_context.set(request_id)
        started_at = perf_counter()
        try:
            response = await call_next(request)
        finally:
            duration_ms = round((perf_counter() - started_at) * 1000, 2)
            logger.info(
                "Request completed",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "request_id": request_id,
                    "duration_ms": duration_ms,
                },
            )
            request_id_context.reset(context_token)

        response.headers["X-Request-ID"] = request_id
        return response


class UploadSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_upload_bytes: int, api_v1_prefix: str) -> None:
        super().__init__(app)
        self._max_upload_bytes = max_upload_bytes
        self._guarded_paths = {
            f"{api_v1_prefix}/documents/upload",
            f"{api_v1_prefix}/documents/analyse",
        }

    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.url.path in self._guarded_paths:
            content_length = request.headers.get("content-length")
            if content_length is not None:
                try:
                    request_size = int(content_length)
                except ValueError:
                    request_size = None
                else:
                    if request_size > self._max_upload_bytes:
                        return JSONResponse(
                            status_code=413,
                            content={
                                "error": {
                                    "code": "request_too_large",
                                    "message": "The upload request exceeds the maximum allowed size.",
                                }
                            },
                        )

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_v1_prefix: str, limiter: RequestRateLimiter) -> None:
        super().__init__(app)
        self._api_v1_prefix = api_v1_prefix
        self._limiter = limiter

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(self._api_v1_prefix):
            decision = self._limiter.evaluate(request)
            if not decision.allowed:
                content = {
                    "error": {
                        "code": "rate_limited",
                        "message": "Too many requests. Please retry later.",
                    }
                }
                response = JSONResponse(status_code=429, content=content)
                if decision.retry_after_seconds is not None:
                    response.headers["Retry-After"] = str(decision.retry_after_seconds)
                for header, value in decision.headers.items():
                    response.headers[header] = value
                return response

            response = await call_next(request)
            for header, value in decision.headers.items():
                response.headers[header] = value
            return response

        return await call_next(request)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(title=app_settings.app_name)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    _configure_optional_features(app, app_settings)
    return app


def _configure_optional_features(app: FastAPI, settings: Settings) -> None:
    try:
        from app.core.logging import configure_logging

        configure_logging()
    except ModuleNotFoundError:
        logger.warning("Optional logging configuration is unavailable.")

    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        RequestContextMiddleware,
    )
    from app.api.deps import get_request_rate_limiter

    app.add_middleware(
        RateLimitMiddleware,
        api_v1_prefix=settings.api_v1_prefix,
        limiter=get_request_rate_limiter(),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Accept", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(
        UploadSizeLimitMiddleware,
        max_upload_bytes=settings.max_upload_bytes,
        api_v1_prefix=settings.api_v1_prefix,
    )

    from app.core.errors import register_exception_handlers

    register_exception_handlers(app)

    from app.api.v1.documents import router as documents_router

    app.include_router(documents_router, prefix=settings.api_v1_prefix)


app = create_app()
