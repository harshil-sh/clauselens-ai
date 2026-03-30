from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.domain.models import DocumentRecord
from app.repositories.interfaces import DocumentRepository
from app.services.file_safety import build_safe_filename
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
        upload_root = Path(self._settings.upload_dir).expanduser().resolve()
        storage_dir = upload_root / document_id
        storage_dir.mkdir(parents=True, exist_ok=True)

        file_path = (storage_dir / build_safe_filename(upload.filename)).resolve()
        file_path.relative_to(storage_dir)
        with file_path.open("xb") as stored_file:
            stored_file.write(upload.content)

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
