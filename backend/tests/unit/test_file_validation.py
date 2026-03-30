from tempfile import SpooledTemporaryFile

from starlette.datastructures import Headers, UploadFile

from app.api.v1.documents import upload_document
from app.core.config import Settings
from app.core.errors import ApiError
from app.services.file_validation import FileValidationService
from app.services.upload_storage import LocalUploadStorageService
from app.repositories.in_memory import InMemoryDocumentRepository


def _build_upload_file(
    filename: str,
    content: bytes,
    content_type: str = "text/plain",
) -> UploadFile:
    file = SpooledTemporaryFile()
    file.write(content)
    file.seek(0)
    return UploadFile(
        filename=filename,
        file=file,
        headers=Headers({"content-type": content_type}),
    )


def test_validate_upload_accepts_supported_file_within_size_limit() -> None:
    service = FileValidationService(Settings(max_upload_mb=1))

    result = _run(service.validate_upload(_build_upload_file("sample.txt", b"contract text")))

    assert result.filename == "sample.txt"
    assert result.content_type == "text/plain"
    assert result.size_bytes == 13
    assert result.content == b"contract text"


def test_validate_upload_accepts_supported_file_with_uppercase_extension() -> None:
    service = FileValidationService(Settings(max_upload_mb=1))

    result = _run(
        service.validate_upload(
            _build_upload_file(
                "MASTER-SERVICE-AGREEMENT.PDF",
                b"%PDF-1.4 mock content",
                content_type="application/pdf",
            )
        )
    )

    assert result.filename == "MASTER-SERVICE-AGREEMENT.PDF"
    assert result.content_type == "application/pdf"
    assert result.size_bytes == len(b"%PDF-1.4 mock content")


def test_validate_upload_rejects_unsupported_file_type() -> None:
    service = FileValidationService(Settings())

    try:
        _run(service.validate_upload(_build_upload_file("sample.exe", b"binary data")))
    except ApiError as exc:
        assert exc.code == "unsupported_file_type"
        assert exc.message == "Only PDF, DOCX, and TXT files are supported."
    else:
        raise AssertionError("Expected ApiError for unsupported file type.")


def test_validate_upload_rejects_empty_file() -> None:
    service = FileValidationService(Settings())

    try:
        _run(service.validate_upload(_build_upload_file("empty.txt", b"")))
    except ApiError as exc:
        assert exc.code == "empty_file"
        assert exc.message == "Uploaded file is empty."
    else:
        raise AssertionError("Expected ApiError for empty upload.")


def test_validate_upload_rejects_missing_filename() -> None:
    service = FileValidationService(Settings())

    try:
        _run(service.validate_upload(_build_upload_file("", b"content")))
    except ApiError as exc:
        assert exc.code == "missing_filename"
        assert exc.message == "Uploaded file must have a filename."
    else:
        raise AssertionError("Expected ApiError for missing filename.")


def test_validate_upload_rejects_file_over_size_limit() -> None:
    service = FileValidationService(Settings(max_upload_mb=1))
    oversized_payload = b"a" * ((1024 * 1024) + 1)

    try:
        _run(service.validate_upload(_build_upload_file("large.txt", oversized_payload)))
    except ApiError as exc:
        assert exc.code == "file_too_large"
        assert exc.message == "The uploaded file exceeds the maximum allowed size."
    else:
        raise AssertionError("Expected ApiError for oversized upload.")


def test_upload_document_returns_metadata_response() -> None:
    settings = Settings(max_upload_mb=1)
    service = FileValidationService(settings)
    storage_service = LocalUploadStorageService(
        settings=settings,
        repository=InMemoryDocumentRepository(),
    )

    response = _run(
        upload_document(
            file=_build_upload_file("sample.txt", b"contract text"),
            validation_service=service,
            storage_service=storage_service,
        )
    )

    assert response.document_id.startswith("doc_")
    assert response.filename == "sample.txt"
    assert response.content_type == "text/plain"
    assert response.size_bytes == 13


def _run(coroutine):
    import asyncio

    return asyncio.run(coroutine)
