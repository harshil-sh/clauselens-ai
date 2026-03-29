from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="ClauseLens AI", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    max_upload_mb: int = Field(default=10, alias="MAX_UPLOAD_MB")
    upload_dir: str = Field(default="./data/uploads", alias="UPLOAD_DIR")
    allowed_file_extensions: str = Field(
        default=".pdf,.docx,.txt",
        alias="ALLOWED_FILE_EXTENSIONS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def allowed_extensions_set(self) -> set[str]:
        return {
            part.strip().lower()
            for part in self.allowed_file_extensions.split(",")
            if part.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
