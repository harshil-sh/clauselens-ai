from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

import pytest

from app.core.errors import ApiError
from app.domain.models import ExtractedDocument
from app.services import text_extraction
from app.services.text_extraction import (
    DocxTextExtractionService,
    PdfTextExtractionService,
    TxtTextExtractionService,
)


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


def test_extract_txt_document_returns_normalized_contract(tmp_path: Path) -> None:
    file_path = tmp_path / "contract.TXT"
    file_path.write_text("  Payment terms apply.  ", encoding="utf-8")

    service = TxtTextExtractionService()

    extracted = service.extract_document(file_path)

    assert extracted == ExtractedDocument(
        filename="contract.TXT",
        file_extension=".txt",
        extracted_text="Payment terms apply.",
        char_count=len("Payment terms apply."),
    )


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


def test_extract_pdf_document_returns_normalized_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    file_path = tmp_path / "contract.pdf"
    file_path.write_bytes(b"%PDF-1.4")

    class FakePage:
        def extract_text(self) -> str | None:
            return "  Renewal is annual.  "

    class FakePdfReader:
        def __init__(self, _: str) -> None:
            self.pages = [FakePage()]

    monkeypatch.setattr(
        text_extraction,
        "import_module",
        lambda name: SimpleNamespace(PdfReader=FakePdfReader) if name == "pypdf" else None,
    )

    service = PdfTextExtractionService()

    extracted = service.extract_document(file_path)

    assert extracted == ExtractedDocument(
        filename="contract.pdf",
        file_extension=".pdf",
        extracted_text="Renewal is annual.",
        char_count=len("Renewal is annual."),
    )


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


def test_extract_docx_text_successfully(tmp_path: Path) -> None:
    file_path = tmp_path / "contract.docx"
    _write_docx(
        file_path,
        """
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
          <w:body>
            <w:p>
              <w:r><w:t xml:space="preserve">  Payment terms apply. </w:t></w:r>
              <w:r><w:tab/></w:r>
              <w:r><w:t>Net 30</w:t></w:r>
            </w:p>
            <w:p>
              <w:r><w:t>Renewal is annual.</w:t></w:r>
              <w:r><w:br/></w:r>
              <w:r><w:t>Notice is required.</w:t></w:r>
            </w:p>
          </w:body>
        </w:document>
        """.strip(),
    )

    service = DocxTextExtractionService()

    extracted = service.extract(file_path)

    assert extracted == "Payment terms apply. \tNet 30\n\nRenewal is annual.\nNotice is required."


def test_extract_docx_rejects_non_docx_files(tmp_path: Path) -> None:
    file_path = tmp_path / "contract.txt"
    file_path.write_text("plain text", encoding="utf-8")

    service = DocxTextExtractionService()

    with pytest.raises(ApiError) as exc_info:
        service.extract(file_path)

    assert exc_info.value.code == "unsupported_file_type"


def test_extract_docx_document_returns_normalized_contract(tmp_path: Path) -> None:
    file_path = tmp_path / "contract.docx"
    _write_docx(
        file_path,
        """
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
          <w:body>
            <w:p><w:r><w:t>  Notice is required.  </w:t></w:r></w:p>
          </w:body>
        </w:document>
        """.strip(),
    )

    service = DocxTextExtractionService()

    extracted = service.extract_document(file_path)

    assert extracted == ExtractedDocument(
        filename="contract.docx",
        file_extension=".docx",
        extracted_text="Notice is required.",
        char_count=len("Notice is required."),
    )


def test_extract_docx_raises_for_invalid_archive(tmp_path: Path) -> None:
    file_path = tmp_path / "contract.docx"
    file_path.write_bytes(b"not a zip archive")

    service = DocxTextExtractionService()

    with pytest.raises(ApiError) as exc_info:
        service.extract(file_path)

    assert exc_info.value.code == "extraction_failed"


def test_extract_docx_raises_when_no_text_is_found(tmp_path: Path) -> None:
    file_path = tmp_path / "contract.docx"
    _write_docx(
        file_path,
        """
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
          <w:body>
            <w:p><w:r><w:t>   </w:t></w:r></w:p>
          </w:body>
        </w:document>
        """.strip(),
    )

    service = DocxTextExtractionService()

    with pytest.raises(ApiError) as exc_info:
        service.extract(file_path)

    assert exc_info.value.code == "extraction_failed"


def _write_docx(file_path: Path, document_xml: str) -> None:
    with ZipFile(file_path, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types></Types>")
        archive.writestr("word/document.xml", document_xml)
