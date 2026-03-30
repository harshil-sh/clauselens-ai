from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from app.domain.models import AnalysisResult, AnalysisSummary, Clause, DocumentRecord, RiskFlag
from app.repositories.interfaces import AnalysisRepository, DocumentRepository


class SQLiteDatabase:
    def __init__(self, db_path: str) -> None:
        self._db_path = Path(db_path).expanduser().resolve()
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    content_type TEXT,
                    storage_path TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS analyses (
                    document_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    summary_short_summary TEXT NOT NULL,
                    summary_key_points_json TEXT NOT NULL,
                    clauses_json TEXT NOT NULL,
                    risk_flags_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )


class SQLiteDocumentRepository(DocumentRepository):
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def save(self, document: DocumentRecord) -> DocumentRecord:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    document_id,
                    filename,
                    content_type,
                    storage_path,
                    created_at
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    filename = excluded.filename,
                    content_type = excluded.content_type,
                    storage_path = excluded.storage_path,
                    created_at = excluded.created_at
                """,
                (
                    document.document_id,
                    document.filename,
                    document.content_type,
                    document.storage_path,
                    document.created_at.isoformat(),
                ),
            )
        return document

    def get_by_id(self, document_id: str) -> DocumentRecord | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT document_id, filename, content_type, storage_path, created_at
                FROM documents
                WHERE document_id = ?
                """,
                (document_id,),
            ).fetchone()

        if row is None:
            return None

        return DocumentRecord(
            document_id=row["document_id"],
            filename=row["filename"],
            content_type=row["content_type"],
            storage_path=row["storage_path"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


class SQLiteAnalysisRepository(AnalysisRepository):
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def save(self, result: AnalysisResult) -> AnalysisResult:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO analyses (
                    document_id,
                    filename,
                    document_type,
                    summary_short_summary,
                    summary_key_points_json,
                    clauses_json,
                    risk_flags_json,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    filename = excluded.filename,
                    document_type = excluded.document_type,
                    summary_short_summary = excluded.summary_short_summary,
                    summary_key_points_json = excluded.summary_key_points_json,
                    clauses_json = excluded.clauses_json,
                    risk_flags_json = excluded.risk_flags_json,
                    created_at = excluded.created_at
                """,
                (
                    result.document_id,
                    result.filename,
                    result.document_type,
                    result.summary.short_summary,
                    json.dumps(result.summary.key_points),
                    json.dumps([self._serialize_clause(clause) for clause in result.clauses]),
                    json.dumps([self._serialize_risk_flag(flag) for flag in result.risk_flags]),
                    result.created_at.isoformat(),
                ),
            )
        return result

    def get_by_id(self, document_id: str) -> AnalysisResult | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    document_id,
                    filename,
                    document_type,
                    summary_short_summary,
                    summary_key_points_json,
                    clauses_json,
                    risk_flags_json,
                    created_at
                FROM analyses
                WHERE document_id = ?
                """,
                (document_id,),
            ).fetchone()

        return self._build_analysis_result(row) if row is not None else None

    def list_recent(self) -> list[AnalysisResult]:
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    document_id,
                    filename,
                    document_type,
                    summary_short_summary,
                    summary_key_points_json,
                    clauses_json,
                    risk_flags_json,
                    created_at
                FROM analyses
                ORDER BY datetime(created_at) DESC, document_id DESC
                """
            ).fetchall()

        return [self._build_analysis_result(row) for row in rows]

    def _build_analysis_result(self, row: sqlite3.Row) -> AnalysisResult:
        return AnalysisResult(
            document_id=row["document_id"],
            filename=row["filename"],
            document_type=row["document_type"],
            summary=AnalysisSummary(
                short_summary=row["summary_short_summary"],
                key_points=list(json.loads(row["summary_key_points_json"])),
            ),
            clauses=[
                Clause(**clause_payload)
                for clause_payload in json.loads(row["clauses_json"])
            ],
            risk_flags=[
                RiskFlag(**risk_flag_payload)
                for risk_flag_payload in json.loads(row["risk_flags_json"])
            ],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _serialize_clause(self, clause: Clause) -> dict[str, object]:
        return {
            "clause_id": clause.clause_id,
            "heading": clause.heading,
            "category": clause.category,
            "extracted_text": clause.extracted_text,
            "confidence": clause.confidence,
            "page_reference": clause.page_reference,
        }

    def _serialize_risk_flag(self, risk_flag: RiskFlag) -> dict[str, object]:
        return {
            "risk_id": risk_flag.risk_id,
            "severity": risk_flag.severity,
            "title": risk_flag.title,
            "description": risk_flag.description,
            "recommendation": risk_flag.recommendation,
            "impacted_clause_id": risk_flag.impacted_clause_id,
        }
