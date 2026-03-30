from __future__ import annotations

from importlib import import_module
from pathlib import Path

from app.core.errors import ApiError


def _normalize_extracted_text(content: str) -> str:
    extracted = content.strip()
    if not extracted:
        raise ApiError(
            code="extraction_failed",
            message="Document text could not be extracted.",
            status_code=400,
        )

    return extracted


class TxtTextExtractionService:
    def extract(self, file_path: str | Path) -> str:
        path = Path(file_path)

        if path.suffix.lower() != ".txt":
            raise ApiError(
                code="unsupported_file_type",
                message="TXT text extraction requires a .txt file.",
                status_code=400,
            )

        try:
            content = path.read_text(encoding="utf-8-sig")
        except FileNotFoundError as exc:
            raise ApiError(
                code="extraction_failed",
                message="Document text could not be extracted.",
                status_code=400,
            ) from exc
        except UnicodeDecodeError as exc:
            raise ApiError(
                code="extraction_failed",
                message="Document text could not be extracted.",
                status_code=400,
            ) from exc

        return _normalize_extracted_text(content)


class PdfTextExtractionService:
    def extract(self, file_path: str | Path) -> str:
        path = Path(file_path)

        if path.suffix.lower() != ".pdf":
            raise ApiError(
                code="unsupported_file_type",
                message="PDF text extraction requires a .pdf file.",
                status_code=400,
            )

        try:
            pypdf = import_module("pypdf")
            reader = pypdf.PdfReader(str(path))
            content = "\n".join((page.extract_text() or "").strip() for page in reader.pages)
        except FileNotFoundError as exc:
            raise ApiError(
                code="extraction_failed",
                message="Document text could not be extracted.",
                status_code=400,
            ) from exc
        except ImportError as exc:
            raise ApiError(
                code="extraction_failed",
                message="Document text could not be extracted.",
                status_code=400,
            ) from exc
        except Exception as exc:
            raise ApiError(
                code="extraction_failed",
                message="Document text could not be extracted.",
                status_code=400,
            ) from exc

        return _normalize_extracted_text(content)
