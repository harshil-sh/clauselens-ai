from pathlib import Path

from app.core.config import Settings
from app.repositories.in_memory import InMemoryDocumentRepository
from app.services.file_validation import ValidatedUpload
from app.services.upload_storage import LocalUploadStorageService


def test_store_persists_upload_and_metadata(tmp_path: Path) -> None:
    repository = InMemoryDocumentRepository()
    service = LocalUploadStorageService(
        settings=Settings(upload_dir=str(tmp_path)),
        repository=repository,
    )

    stored = service.store(
        ValidatedUpload(
            filename="Master Services Agreement.TXT",
            content_type="text/plain",
            size_bytes=16,
            content=b"contract content",
        )
    )

    assert stored.document_id.startswith("doc_")
    assert stored.filename == "Master Services Agreement.TXT"
    document = repository.get_by_id(stored.document_id)
    assert document is not None
    assert document.storage_path is not None
    saved_path = Path(document.storage_path)
    assert saved_path.exists()
    assert saved_path.read_bytes() == b"contract content"
    assert saved_path.parent == tmp_path / stored.document_id
    assert saved_path.name == "Master-Services-Agreement.txt"


def test_store_strips_nested_paths_from_filename(tmp_path: Path) -> None:
    repository = InMemoryDocumentRepository()
    service = LocalUploadStorageService(
        settings=Settings(upload_dir=str(tmp_path)),
        repository=repository,
    )

    stored = service.store(
        ValidatedUpload(
            filename="../../contracts/final?.pdf",
            content_type="application/pdf",
            size_bytes=7,
            content=b"content",
        )
    )

    document = repository.get_by_id(stored.document_id)
    assert document is not None
    assert document.storage_path is not None
    saved_path = Path(document.storage_path)
    assert saved_path.name == "final.pdf"


def test_store_strips_windows_paths_from_filename(tmp_path: Path) -> None:
    repository = InMemoryDocumentRepository()
    service = LocalUploadStorageService(
        settings=Settings(upload_dir=str(tmp_path)),
        repository=repository,
    )

    stored = service.store(
        ValidatedUpload(
            filename=r"..\..\contracts\msa final?.DOCX",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size_bytes=7,
            content=b"content",
        )
    )

    document = repository.get_by_id(stored.document_id)
    assert document is not None
    assert document.storage_path is not None
    saved_path = Path(document.storage_path)
    assert saved_path.name == "msa-final.docx"
