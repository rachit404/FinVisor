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


INSTRUMENT_ID = "TEST:NSE:SBIN:SNAPSHOT"


def create_candle(
    timestamp: datetime,
    close: str,
) -> Candle:
    return Candle(
        identity=CandleIdentity(
            instrument_id=INSTRUMENT_ID,
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


def test_snapshot_is_deterministic():
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

    sync_candles(
        INSTRUMENT_ID,
        CandleInterval.FIVE_MINUTES,
        candles,
    )

    first_snapshot = create_market_snapshot(
        INSTRUMENT_ID,
        CandleInterval.FIVE_MINUTES,
    )

    second_snapshot = create_market_snapshot(
        INSTRUMENT_ID,
        CandleInterval.FIVE_MINUTES,
    )

    assert len(first_snapshot.candles) == 2
    assert (
        first_snapshot.snapshot_hash
        == second_snapshot.snapshot_hash
    )

    assert (
        first_snapshot.data_version
        == second_snapshot.data_version
    )