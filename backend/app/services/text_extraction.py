from __future__ import annotations

from pathlib import Path

from app.core.errors import ApiError


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

        extracted = content.strip()
        if not extracted:
            raise ApiError(
                code="extraction_failed",
                message="Document text could not be extracted.",
                status_code=400,
            )

        return extracted
