import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


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
        CORSMiddleware,
        allow_origins=list(settings.cors_allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Accept", "Content-Type"],
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
