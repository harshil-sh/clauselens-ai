import asyncio
from datetime import datetime
from io import BytesIO

from fastapi import UploadFile

from app.api.v1.documents import analyse_document
from app.domain.models import AnalysisResult, AnalysisSummary, Clause, ExtractedDocument, RiskFlag
from app.services.file_validation import ValidatedUpload


class StubValidationService:
    async def validate_upload(self, file: UploadFile) -> ValidatedUpload:
        assert file.filename == "contract.txt"
        return ValidatedUpload(
            filename="contract.txt",
            content_type="text/plain",
            size_bytes=12,
            content=b"raw content",
        )


class StubExtractionService:
    def extract(self, upload: ValidatedUpload) -> ExtractedDocument:
        assert upload.filename == "contract.txt"
        return ExtractedDocument(
            filename="contract.txt",
            file_extension=".txt",
            extracted_text="Normalized contract text.",
            char_count=len("Normalized contract text."),
        )


class StubAnalysisService:
    def analyse(self, filename: str, document_text: str) -> AnalysisResult:
        assert filename == "contract.txt"
        assert document_text == "Normalized contract text."
        return AnalysisResult(
            document_id="doc_123",
            filename=filename,
            document_type="contract",
            summary=AnalysisSummary(
                short_summary="Short summary",
                key_points=["Point 1", "Point 2"],
            ),
            clauses=[
                Clause(
                    clause_id="clause_1",
                    heading="Termination",
                    category="termination",
                    extracted_text="Either party may terminate for breach.",
                    confidence=0.91,
                    page_reference=2,
                )
            ],
            risk_flags=[
                RiskFlag(
                    risk_id="risk_1",
                    severity="medium",
                    title="Termination rights are narrow",
                    description="The clause allows termination only for breach.",
                    recommendation="Confirm whether convenience termination is needed.",
                    impacted_clause_id="clause_1",
                )
            ],
            created_at=datetime(2026, 3, 30, 10, 0, 0),
        )


def test_analyse_document_returns_structured_response() -> None:
    response = asyncio.run(
        analyse_document(
            file=UploadFile(filename="contract.txt", file=BytesIO(b"ignored")),
            validation_service=StubValidationService(),
            extraction_service=StubExtractionService(),
            service=StubAnalysisService(),
        )
    )

    assert response.document_id == "doc_123"
    assert response.filename == "contract.txt"
    assert response.document_type == "contract"
    assert response.summary.short_summary == "Short summary"
    assert response.summary.key_points == ["Point 1", "Point 2"]
    assert response.clauses[0].clause_id == "clause_1"
    assert response.clauses[0].page_reference == 2
    assert response.risk_flags[0].impacted_clause_id == "clause_1"
