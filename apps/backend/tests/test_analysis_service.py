from datetime import datetime
from decimal import Decimal

from app.domain.market import (
    Candle,
    CandleIdentity,
    CandleInterval,
    MarketDataSnapshot,
)
from app.services.analysis_service import run_analysis
from app.storage.analysis_repository import get_analysis
from app.storage.database import initialize_database
from app.storage.market_snapshot_repository import save_snapshot


def test_run_analysis_creates_immutable_record():
    initialize_database()

    snapshot = MarketDataSnapshot(
        instrument_id="TEST:NSE:SBIN:AI",
        interval=CandleInterval.FIVE_MINUTES,
        data_version=7,
        latest_candle_timestamp=datetime(
            2026,
            8,
            28,
            9,
            15,
        ),
        candles=(
            Candle(
                identity=CandleIdentity(
                    instrument_id="TEST:NSE:SBIN:AI",
                    interval=CandleInterval.FIVE_MINUTES,
                    timestamp=datetime(
                        2026,
                        8,
                        28,
                        9,
                        15,
                    ),
                ),
                open=Decimal("100"),
                high=Decimal("110"),
                low=Decimal("90"),
                close=Decimal("105"),
                volume=1000,
                source="test",
                fetched_at=datetime(
                    2026,
                    8,
                    28,
                    9,
                    16,
                ),
            ),
        ),
        snapshot_hash="test-ai-snapshot-001",
    )

    save_snapshot(snapshot)

    result = run_analysis(
        snapshot_hash=snapshot.snapshot_hash,
        prompt="Analyze this stock.",
        model="test-model",
        response="The trend is neutral.",
    )

    assert result is not None

    analysis = result.analysis

    assert analysis.snapshot_hash == snapshot.snapshot_hash
    assert analysis.instrument_id == snapshot.instrument_id
    assert analysis.data_version == 7
    assert analysis.prompt == "Analyze this stock."
    assert analysis.response == "The trend is neutral."

    restored = get_analysis(
        analysis.analysis_id
    )

    assert restored == analysis


def test_run_analysis_returns_none_for_missing_snapshot():
    initialize_database()

    result = run_analysis(
        snapshot_hash="missing-snapshot",
        prompt="Analyze this stock.",
        model="test-model",
        response="This should not be saved.",
    )

    assert result is None