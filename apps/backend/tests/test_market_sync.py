from datetime import datetime
from decimal import Decimal

from app.domain.market import (
    Candle,
    CandleIdentity,
    CandleInterval,
)

from app.services.market_sync import sync_candles
from app.storage.database import initialize_database


def create_candle(
    timestamp: datetime,
    close: str,
) -> Candle:
    return Candle(
        identity=CandleIdentity(
            instrument_id="TEST:NSE:SBIN:SYNC",
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


def test_sync_detects_new_and_duplicate_data():
    initialize_database()

    candles = [
        create_candle(
            datetime(2026, 8, 28, 9, 15),
            "101",
        ),
        create_candle(
            datetime(2026, 8, 28, 9, 20),
            "102",
        ),
    ]

    first_sync = sync_candles(
        "TEST:NSE:SBIN:SYNC",
        CandleInterval.FIVE_MINUTES,
        candles,
    )

    assert first_sync.inserted == 2
    assert first_sync.updated == 0
    assert first_sync.unchanged == 0
    assert first_sync.new_data_available is True

    second_sync = sync_candles(
        "TEST:NSE:SBIN:SYNC",
        CandleInterval.FIVE_MINUTES,
        candles,
    )

    assert second_sync.inserted == 0
    assert second_sync.updated == 0
    assert second_sync.unchanged == 2
    assert second_sync.new_data_available is False