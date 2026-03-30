from pathlib import Path
from types import SimpleNamespace

import pytest

from app.core.errors import ApiError
from app.services import text_extraction
from app.services.text_extraction import PdfTextExtractionService, TxtTextExtractionService


def test_extract_txt_text_successfully(tmp_path: Path) -> None:
    file_path = tmp_path / "contract.txt"
    file_path.write_text("  Payment terms apply.\nRenewal is annual.  ", encoding="utf-8")

    service = TxtTextExtractionService()

    extracted = service.extract(file_path)

    assert extracted == "Payment terms apply.\nRenewal is annual."


def test_extract_txt_text_strips_utf8_bom(tmp_path: Path) -> None:
    file_path = tmp_path / "contract.txt"
    file_path.write_bytes(b"\xef\xbb\xbfTermination clause")

    service = TxtTextExtractionService()

    extracted = service.extract(file_path)

    assert extracted == "Termination clause"


def test_extract_rejects_non_txt_files(tmp_path: Path) -> None:
    file_path = tmp_path / "contract.pdf"
    file_path.write_text("not actually a pdf", encoding="utf-8")

    service = TxtTextExtractionService()

    with pytest.raises(ApiError) as exc_info:
        service.extract(file_path)

    assert exc_info.value.code == "unsupported_file_type"


def test_extract_raises_for_invalid_utf8_content(tmp_path: Path) -> None:
    file_path = tmp_path / "contract.txt"
    file_path.write_bytes(b"\xff\xfe\x00")

    service = TxtTextExtractionService()

    with pytest.raises(ApiError) as exc_info:
        service.extract(file_path)

    assert exc_info.value.code == "extraction_failed"


def test_extract_pdf_text_successfully(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    file_path = tmp_path / "contract.pdf"
    file_path.write_bytes(b"%PDF-1.4")

    class FakePage:
        def __init__(self, text: str | None) -> None:
            self._text = text

        def extract_text(self) -> str | None:
            return self._text

    class FakePdfReader:
        def __init__(self, _: str) -> None:
            self.pages = [
                FakePage("  Payment terms apply.  "),
                FakePage(None),
                FakePage("Renewal is annual."),
            ]

    monkeypatch.setattr(
        text_extraction,
        "import_module",
        lambda name: SimpleNamespace(PdfReader=FakePdfReader) if name == "pypdf" else None,
    )

    service = PdfTextExtractionService()

    extracted = service.extract(file_path)

    assert extracted == "Payment terms apply.\n\nRenewal is annual."


def test_extract_pdf_rejects_non_pdf_files(tmp_path: Path) -> None:
    file_path = tmp_path / "contract.txt"
    file_path.write_text("plain text", encoding="utf-8")

    service = PdfTextExtractionService()

    with pytest.raises(ApiError) as exc_info:
        service.extract(file_path)

    assert exc_info.value.code == "unsupported_file_type"


def test_extract_pdf_raises_when_parser_is_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    file_path = tmp_path / "contract.pdf"
    file_path.write_bytes(b"%PDF-1.4")

    def raise_import_error(_: str) -> None:
        raise ImportError("pypdf is not installed")

    monkeypatch.setattr(text_extraction, "import_module", raise_import_error)

    service = PdfTextExtractionService()

    with pytest.raises(ApiError) as exc_info:
        service.extract(file_path)

    assert exc_info.value.code == "extraction_failed"


def test_extract_pdf_raises_when_no_text_is_found(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    file_path = tmp_path / "contract.pdf"
    file_path.write_bytes(b"%PDF-1.4")

    class FakePage:
        def extract_text(self) -> str | None:
            return "   "

    class FakePdfReader:
        def __init__(self, _: str) -> None:
            self.pages = [FakePage()]

    monkeypatch.setattr(
        text_extraction,
        "import_module",
        lambda name: SimpleNamespace(PdfReader=FakePdfReader) if name == "pypdf" else None,
    )

    service = PdfTextExtractionService()

    with pytest.raises(ApiError) as exc_info:
        service.extract(file_path)

    assert exc_info.value.code == "extraction_failed"
