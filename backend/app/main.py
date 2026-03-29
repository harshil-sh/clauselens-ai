import logging

from fastapi import FastAPI

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


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
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.core.errors import register_exception_handlers

    register_exception_handlers(app)

    from app.api.v1.documents import router as documents_router

    app.include_router(documents_router, prefix=settings.api_v1_prefix)


app = create_app()
