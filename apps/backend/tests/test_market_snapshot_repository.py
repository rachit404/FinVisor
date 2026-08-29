from datetime import datetime
from decimal import Decimal

from app.domain.market import (
    Candle,
    CandleIdentity,
    CandleInterval,
    MarketDataSnapshot,
)
from app.storage.database import initialize_database
from app.storage.market_snapshot_repository import (
    get_snapshot,
    save_snapshot,
)


def test_snapshot_can_be_saved_and_restored():
    initialize_database()

    snapshot = MarketDataSnapshot(
        instrument_id="TEST:NSE:SBIN:PERSIST",
        interval=CandleInterval.FIVE_MINUTES,
        data_version=1,
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
                    instrument_id="TEST:NSE:SBIN:PERSIST",
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
        snapshot_hash="test-snapshot-hash-001",
    )

    save_snapshot(snapshot)

    restored = get_snapshot(
        "test-snapshot-hash-001"
    )

    assert restored is not None
    assert restored.snapshot_hash == snapshot.snapshot_hash
    assert restored.instrument_id == snapshot.instrument_id
    assert restored.data_version == snapshot.data_version
    assert restored.candles == snapshot.candles


def test_duplicate_snapshot_is_not_created():
    initialize_database()

    snapshot = MarketDataSnapshot(
        instrument_id="TEST:NSE:SBIN:DUPLICATE",
        interval=CandleInterval.FIVE_MINUTES,
        data_version=1,
        latest_candle_timestamp=None,
        candles=(),
        snapshot_hash="test-duplicate-snapshot",
    )

    save_snapshot(snapshot)
    save_snapshot(snapshot)

    restored = get_snapshot(
        "test-duplicate-snapshot"
    )

    assert restored is not None
    assert restored.snapshot_hash == snapshot.snapshot_hash