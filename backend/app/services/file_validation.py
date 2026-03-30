from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings
from app.core.errors import ApiError


@dataclass
class ValidatedUpload:
    filename: str
    content_type: str | None
    size_bytes: int
    content: bytes


class FileValidationService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def validate_upload(self, file: UploadFile) -> ValidatedUpload:
        if not file.filename:
            raise ApiError(code="missing_filename", message="Uploaded file must have a filename.", status_code=400)

        extension = Path(file.filename).suffix.lower()
        if extension not in self.settings.allowed_extensions_set:
            raise ApiError(
                code="unsupported_file_type",
                message="Only PDF, DOCX, and TXT files are supported.",
                status_code=400,
            )

        file.file.seek(0)
        content = file.file.read()
        size_bytes = len(content)

        if size_bytes == 0:
            raise ApiError(code="empty_file", message="Uploaded file is empty.", status_code=400)

        if size_bytes > self.settings.max_upload_bytes:
            raise ApiError(
                code="file_too_large",
                message="The uploaded file exceeds the maximum allowed size.",
                status_code=400,
            )

        return ValidatedUpload(
            filename=file.filename,
            content_type=file.content_type,
            size_bytes=size_bytes,
            content=content,
        )
