import asyncio
import json

import pytest
from pydantic import ValidationError

from app.core.config import Settings, clear_settings_cache, get_settings
from app.main import create_app


@pytest.fixture(autouse=True)
def reset_settings_cache() -> None:
    clear_settings_cache()
    yield
    clear_settings_cache()


def test_settings_default_values() -> None:
    settings = get_settings()

    assert settings.app_name == "ClauseLens AI"
    assert settings.app_env == "local"
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.openai_model == "gpt-4.1-mini"
    assert settings.openai_api_key is None
    assert settings.sqlite_db_path == "./data/clauselens.db"
    assert settings.allowed_file_extensions == (".pdf", ".docx", ".txt")
    assert settings.allowed_extensions_set == {".pdf", ".docx", ".txt"}
    assert settings.max_upload_bytes == 10 * 1024 * 1024
    assert settings.cors_allowed_origins == (
        "http://localhost:3000",
        "http://localhost:5173",
    )


def test_settings_reads_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_NAME", "ClauseLens Test")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("API_V1_PREFIX", "/internal/v1/")
    monkeypatch.setenv("ALLOWED_FILE_EXTENSIONS", "pdf,.DOCX,.txt,.txt")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://example.com, https://app.example.com")
    monkeypatch.setenv("MAX_UPLOAD_MB", "25")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1")
    monkeypatch.setenv("OPENAI_API_KEY", "secret-key")
    monkeypatch.setenv("SQLITE_DB_PATH", "/tmp/clauselens-test.db")

    settings = get_settings()

    assert settings.app_name == "ClauseLens Test"
    assert settings.app_env == "test"
    assert settings.api_v1_prefix == "/internal/v1"
    assert settings.openai_model == "gpt-4.1"
    assert settings.openai_api_key == "secret-key"
    assert settings.sqlite_db_path == "/tmp/clauselens-test.db"
    assert settings.allowed_file_extensions == (".pdf", ".docx", ".txt")
    assert settings.cors_allowed_origins == (
        "https://example.com",
        "https://app.example.com",
    )
    assert settings.max_upload_bytes == 25 * 1024 * 1024


def test_invalid_settings_raise_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "invalid")

    with pytest.raises(ValidationError):
        get_settings()


def test_create_app_uses_injected_settings() -> None:
    app = create_app(
        Settings(
            app_name="Custom ClauseLens",
            api_v1_prefix="/custom",
            cors_allowed_origins=("https://ui.example.com",),
        )
    )
    route_paths = {route.path for route in app.routes if hasattr(route, "path")}

    assert app.title == "Custom ClauseLens"
    assert "/custom/documents" in route_paths


def test_create_app_applies_cors_policy_from_settings() -> None:
    app = create_app(
        Settings(
            api_v1_prefix="/api/v1",
            cors_allowed_origins=("https://ui.example.com",),
        )
    )

    messages = _run_request(
        app,
        method="OPTIONS",
        path="/api/v1/documents",
        headers=[
            (b"origin", b"https://ui.example.com"),
            (b"access-control-request-method", b"GET"),
        ],
    )
    response_start = next(
        message for message in messages if message["type"] == "http.response.start"
    )
    response_headers = {
        key.decode("latin-1"): value.decode("latin-1")
        for key, value in response_start["headers"]
    }

    assert response_start["status"] == 200
    assert response_headers["access-control-allow-origin"] == "https://ui.example.com"
    assert response_headers["access-control-allow-methods"] == "GET, POST, OPTIONS"
    assert "access-control-allow-credentials" not in response_headers


def test_create_app_rejects_upload_requests_over_limit_before_body_is_read() -> None:
    app = create_app(Settings(api_v1_prefix="/api/v1", max_upload_mb=1))
    messages = _run_request(
        app,
        method="POST",
        path="/api/v1/documents/upload",
        headers=[(b"content-length", str((1024 * 1024) + 1).encode("ascii"))],
    )
    response_start = next(
        message for message in messages if message["type"] == "http.response.start"
    )
    response_body = next(
        message for message in messages if message["type"] == "http.response.body"
    )

    assert response_start["status"] == 413
    assert json.loads(response_body["body"]) == {
        "error": {
            "code": "request_too_large",
            "message": "The upload request exceeds the maximum allowed size.",
        }
    }


def test_invalid_cors_origins_raise_validation_error() -> None:
    with pytest.raises(ValidationError):
        Settings(cors_allowed_origins=("ui.example.com",))


def _run_request(
    app,
    *,
    method: str,
    path: str,
    headers: list[tuple[bytes, bytes]] | None = None,
) -> list[dict[str, object]]:
    messages: list[dict[str, object]] = []

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": headers or [],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    asyncio.run(app(scope, receive, send))
    return messages
