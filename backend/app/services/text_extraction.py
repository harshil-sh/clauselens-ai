from __future__ import annotations

from importlib import import_module
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from app.core.errors import ApiError
from app.domain.models import ExtractedDocument
from app.services.file_validation import ValidatedUpload


WORDPROCESSINGML_NAMESPACE = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def _normalize_extracted_text(content: str) -> str:
    extracted = content.strip()
    if not extracted:
        raise ApiError(
            code="extraction_failed",
            message="Document text could not be extracted.",
            status_code=400,
        )

    return extracted


def _build_extracted_document(file_path: str | Path, extracted_text: str) -> ExtractedDocument:
    path = Path(file_path)
    return ExtractedDocument(
        filename=path.name,
        file_extension=path.suffix.lower(),
        extracted_text=extracted_text,
        char_count=len(extracted_text),
    )


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

    def extract_document(self, file_path: str | Path) -> ExtractedDocument:
        extracted_text = self.extract(file_path)
        return _build_extracted_document(file_path, extracted_text)


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

    def extract_document(self, file_path: str | Path) -> ExtractedDocument:
        extracted_text = self.extract(file_path)
        return _build_extracted_document(file_path, extracted_text)


class DocxTextExtractionService:
    def extract(self, file_path: str | Path) -> str:
        path = Path(file_path)

        if path.suffix.lower() != ".docx":
            raise ApiError(
                code="unsupported_file_type",
                message="DOCX text extraction requires a .docx file.",
                status_code=400,
            )

        try:
            with ZipFile(path) as archive:
                document_xml = archive.read("word/document.xml")
        except FileNotFoundError as exc:
            raise ApiError(
                code="extraction_failed",
                message="Document text could not be extracted.",
                status_code=400,
            ) from exc
        except (BadZipFile, KeyError, ValueError) as exc:
            raise ApiError(
                code="extraction_failed",
                message="Document text could not be extracted.",
                status_code=400,
            ) from exc

        try:
            root = ElementTree.fromstring(document_xml)
        except ElementTree.ParseError as exc:
            raise ApiError(
                code="extraction_failed",
                message="Document text could not be extracted.",
                status_code=400,
            ) from exc

        paragraphs: list[str] = []
        for paragraph in root.findall(".//w:body/w:p", WORDPROCESSINGML_NAMESPACE):
            segments: list[str] = []
            for node in paragraph.iter():
                tag = node.tag
                if tag == "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t":
                    segments.append(node.text or "")
                elif tag == "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tab":
                    segments.append("\t")
                elif tag in {
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}br",
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cr",
                }:
                    segments.append("\n")

            paragraph_text = "".join(segments).strip()
            if paragraph_text:
                paragraphs.append(paragraph_text)

        return _normalize_extracted_text("\n\n".join(paragraphs))

    def extract_document(self, file_path: str | Path) -> ExtractedDocument:
        extracted_text = self.extract(file_path)
        return _build_extracted_document(file_path, extracted_text)


class UploadedDocumentTextExtractionService:
    def __init__(
        self,
        txt_service: TxtTextExtractionService | None = None,
        pdf_service: PdfTextExtractionService | None = None,
        docx_service: DocxTextExtractionService | None = None,
    ) -> None:
        self._extractors = {
            ".txt": txt_service or TxtTextExtractionService(),
            ".pdf": pdf_service or PdfTextExtractionService(),
            ".docx": docx_service or DocxTextExtractionService(),
        }

    def extract(self, upload: ValidatedUpload) -> ExtractedDocument:
        extension = Path(upload.filename).suffix.lower()
        extractor = self._extractors.get(extension)
        if extractor is None:
            raise ApiError(
                code="unsupported_file_type",
                message="Only PDF, DOCX, and TXT files are supported.",
                status_code=400,
            )

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / Path(upload.filename).name
            temp_path.write_bytes(upload.content)
            return extractor.extract_document(temp_path)
