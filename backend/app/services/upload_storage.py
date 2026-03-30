from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.domain.models import DocumentRecord
from app.repositories.interfaces import DocumentRepository
from app.services.file_validation import ValidatedUpload


@dataclass
class StoredUpload:
    document_id: str
    filename: str
    content_type: str | None
    size_bytes: int


class LocalUploadStorageService:
    def __init__(self, settings: Settings, repository: DocumentRepository) -> None:
        self._settings = settings
        self._repository = repository

    def store(self, upload: ValidatedUpload) -> StoredUpload:
        document_id = f"doc_{uuid4().hex[:12]}"
        storage_dir = Path(self._settings.upload_dir).expanduser().resolve() / document_id
        storage_dir.mkdir(parents=True, exist_ok=True)

        safe_filename = self._build_safe_filename(upload.filename)
        file_path = storage_dir / safe_filename
        file_path.write_bytes(upload.content)

        self._repository.save(
            DocumentRecord(
                document_id=document_id,
                filename=upload.filename,
                content_type=upload.content_type,
                storage_path=str(file_path),
            )
        )
        return StoredUpload(
            document_id=document_id,
            filename=upload.filename,
            content_type=upload.content_type,
            size_bytes=upload.size_bytes,
        )

    def _build_safe_filename(self, filename: str) -> str:
        source = Path(filename).name
        suffix = Path(source).suffix.lower()
        stem = Path(source).stem
        normalized_stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("._-")
        if not normalized_stem:
            normalized_stem = "upload"
        return f"{normalized_stem}{suffix}"
