import logging

from fastapi import FastAPI


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="ClauseLens AI")

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    _configure_optional_features(app)
    return app


def _configure_optional_features(app: FastAPI) -> None:
    try:
        from app.core.logging import configure_logging

        configure_logging()
    except ModuleNotFoundError:
        logger.warning("Optional logging configuration is unavailable.")

    try:
        from app.core.config import get_settings

        settings = get_settings()
        app.title = settings.app_name

        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://localhost:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        from app.core.errors import register_exception_handlers

        register_exception_handlers(app)

        from app.api.v1.documents import router as documents_router

        app.include_router(documents_router, prefix=settings.api_v1_prefix)
    except ModuleNotFoundError:
        logger.warning("Optional application integrations are unavailable.")


app = create_app()
