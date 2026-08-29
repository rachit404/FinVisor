from app.domain.analysis import AnalysisRecord
from app.storage.database import get_connection


def save_analysis(
    analysis: AnalysisRecord,
) -> None:
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_records (
                analysis_id TEXT PRIMARY KEY,
                snapshot_hash TEXT NOT NULL,
                instrument_id TEXT NOT NULL,
                data_version INTEGER NOT NULL,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                model TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            INSERT INTO analysis_records (
                analysis_id,
                snapshot_hash,
                instrument_id,
                data_version,
                prompt,
                response,
                model,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                analysis.analysis_id,
                analysis.snapshot_hash,
                analysis.instrument_id,
                analysis.data_version,
                analysis.prompt,
                analysis.response,
                analysis.model,
                analysis.created_at.isoformat(),
            ),
        )

        connection.commit()

    finally:
        connection.close()


def get_analysis(
    analysis_id: str,
) -> AnalysisRecord | None:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM analysis_records
            WHERE analysis_id = ?
            """,
            (analysis_id,),
        ).fetchone()

        if row is None:
            return None

        from datetime import datetime

        return AnalysisRecord(
            analysis_id=row["analysis_id"],
            snapshot_hash=row["snapshot_hash"],
            instrument_id=row["instrument_id"],
            data_version=row["data_version"],
            prompt=row["prompt"],
            response=row["response"],
            model=row["model"],
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
        )

    finally:
        connection.close()
        
        
        