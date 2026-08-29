from datetime import datetime
from decimal import Decimal

from app.domain.market import (
    Candle,
    CandleIdentity,
    CandleInterval,
)
from app.services.market_snapshot import (
    create_market_snapshot,
)
from app.services.market_sync import sync_candles
from app.storage.database import initialize_database
from app.storage.market_snapshot_repository import (
    get_snapshot,
)


def create_candle(
    instrument_id: str,
    timestamp: datetime,
    close: str,
) -> Candle:
    return Candle(
        identity=CandleIdentity(
            instrument_id=instrument_id,
            interval=CandleInterval.FIVE_MINUTES,
            timestamp=timestamp,
        ),
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal(close),
        volume=1000,
        source="test",
        fetched_at=datetime(2026, 8, 28, 10, 0),
    )


def test_sync_creates_persisted_snapshot():
    initialize_database()

    instrument_id = "TEST:NSE:SBIN:SYNC-SNAPSHOT-ONE"

    sync_candles(
        instrument_id,
        CandleInterval.FIVE_MINUTES,
        [
            create_candle(
                instrument_id,
                datetime(2026, 8, 28, 9, 15),
                "101",
            ),
        ],
    )

    snapshot = create_market_snapshot(
        instrument_id,
        CandleInterval.FIVE_MINUTES,
    )

    restored = get_snapshot(
        snapshot.snapshot_hash,
    )

    assert restored is not None
    assert restored.snapshot_hash == snapshot.snapshot_hash


def test_duplicate_sync_does_not_create_new_snapshot():
    initialize_database()

    instrument_id = "TEST:NSE:SBIN:SYNC-SNAPSHOT-TWO"

    candles = [
        create_candle(
            instrument_id,
            datetime(2026, 8, 28, 9, 15),
            "101",
        ),
    ]

    first_result = sync_candles(
        instrument_id,
        CandleInterval.FIVE_MINUTES,
        candles,
    )

    second_result = sync_candles(
        instrument_id,
        CandleInterval.FIVE_MINUTES,
        candles,
    )

    assert first_result.new_data_available is True
    assert second_result.new_data_available is False