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

    settings = get_settings()

    assert settings.app_name == "ClauseLens Test"
    assert settings.app_env == "test"
    assert settings.api_v1_prefix == "/internal/v1"
    assert settings.openai_model == "gpt-4.1"
    assert settings.openai_api_key == "secret-key"
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
