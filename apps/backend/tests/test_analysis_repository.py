from datetime import datetime

from app.domain.analysis import AnalysisRecord
from app.storage.database import initialize_database
from app.storage.analysis_repository import (
    get_analysis,
    save_analysis,
)


def test_analysis_can_be_saved_and_restored():
    initialize_database()

    analysis = AnalysisRecord(
        analysis_id="test-analysis-001",
        snapshot_hash="test-snapshot-hash",
        instrument_id="NSE:SBIN",
        data_version=3,
        prompt="Should I buy this stock?",
        response="Analysis based on the supplied market data.",
        model="test-model",
        created_at=datetime(
            2026,
            8,
            28,
            12,
            0,
        ),
    )

    save_analysis(analysis)

    restored = get_analysis(
        "test-analysis-001"
    )

    assert restored is not None
    assert restored == analysis


def test_missing_analysis_returns_none():
    initialize_database()

    restored = get_analysis(
        "analysis-that-does-not-exist"
    )

    assert restored is None
    
    
    