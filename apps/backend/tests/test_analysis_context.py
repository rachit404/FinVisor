from datetime import datetime
from decimal import Decimal

from app.domain.market import (
    Candle,
    CandleIdentity,
    CandleInterval,
    MarketDataSnapshot,
)
from app.services.analysis_context import (
    load_analysis_context,
)
from app.storage.database import initialize_database
from app.storage.market_snapshot_repository import (
    save_snapshot,
)


def test_load_analysis_context_from_snapshot():
    initialize_database()

    snapshot = MarketDataSnapshot(
        instrument_id="TEST:NSE:SBIN:ANALYSIS",
        interval=CandleInterval.FIVE_MINUTES,
        data_version=5,
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
                    instrument_id="TEST:NSE:SBIN:ANALYSIS",
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
        snapshot_hash="test-analysis-snapshot-001",
    )

    save_snapshot(snapshot)

    context = load_analysis_context(
        "test-analysis-snapshot-001"
    )

    assert context is not None
    assert context.snapshot_hash == snapshot.snapshot_hash
    assert context.instrument_id == snapshot.instrument_id
    assert context.data_version == 5
    assert context.snapshot == snapshot


def test_missing_snapshot_returns_none():
    initialize_database()

    context = load_analysis_context(
        "snapshot-that-does-not-exist"
    )

    assert context is None
    
    
    