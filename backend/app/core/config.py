from functools import lru_cache
from typing import Annotated, Literal
from urllib.parse import urlparse

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="ClauseLens AI", alias="APP_NAME")
    app_env: Literal["local", "development", "test", "staging", "production"] = Field(
        default="local",
        alias="APP_ENV",
    )
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    max_upload_mb: int = Field(default=10, alias="MAX_UPLOAD_MB", gt=0)
    sqlite_db_path: str = Field(default="./data/clauselens.db", alias="SQLITE_DB_PATH")
    upload_dir: str = Field(default="./data/uploads", alias="UPLOAD_DIR")
    allowed_file_extensions: Annotated[tuple[str, ...], NoDecode] = Field(
        default=(".pdf", ".docx", ".txt"),
        alias="ALLOWED_FILE_EXTENSIONS",
    )
    cors_allowed_origins: Annotated[tuple[str, ...], NoDecode] = Field(
        default=("http://localhost:3000", "http://localhost:5173"),
        alias="CORS_ALLOWED_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("api_v1_prefix")
    @classmethod
    def validate_api_v1_prefix(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("API_V1_PREFIX must start with '/'.")
        return value.rstrip("/") or "/"

    @field_validator("sqlite_db_path", "upload_dir")
    @classmethod
    def validate_non_empty_path(cls, value: str, info: ValidationInfo) -> str:
        if not value.strip():
            raise ValueError(f"{info.field_name.upper()} must not be empty.")
        return value

    @field_validator("allowed_file_extensions", "cors_allowed_origins", mode="before")
    @classmethod
    def parse_comma_separated_values(
        cls,
        value: str | tuple[str, ...] | list[str],
        info: ValidationInfo,
    ) -> tuple[str, ...]:
        if isinstance(value, str):
            items = tuple(part.strip() for part in value.split(",") if part.strip())
        else:
            items = tuple(str(part).strip() for part in value if str(part).strip())

        if not items:
            raise ValueError(f"{info.field_name} must contain at least one value.")
        return items

    @field_validator("allowed_file_extensions")
    @classmethod
    def normalize_allowed_file_extensions(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = []
        for extension in value:
            cleaned = extension.lower()
            normalized.append(cleaned if cleaned.startswith(".") else f".{cleaned}")
        return tuple(dict.fromkeys(normalized))

    @field_validator("cors_allowed_origins")
    @classmethod
    def validate_cors_allowed_origins(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = []
        for origin in value:
            cleaned = origin.rstrip("/")
            parsed = urlparse(cleaned)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError("cors_allowed_origins entries must be absolute http(s) origins.")
            normalized.append(cleaned)
        return tuple(dict.fromkeys(normalized))

    @property
    def allowed_extensions_set(self) -> set[str]:
        return set(self.allowed_file_extensions)

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
