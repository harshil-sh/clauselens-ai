from pathlib import Path

import pytest

from app.core.errors import ApiError
from app.services.text_extraction import TxtTextExtractionService


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
