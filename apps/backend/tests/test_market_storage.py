from datetime import datetime
from decimal import Decimal

from app.domain.market import (
    Candle,
    CandleIdentity,
    CandleInterval,
)

from app.storage.database import initialize_database
from app.storage.market_repository import (
    get_watermark,
    upsert_candle,
)


def test_candle_duplicate_protection():
    initialize_database()

    candle = Candle(
        identity=CandleIdentity(
            instrument_id="NSE:SBIN",
            interval=CandleInterval.FIVE_MINUTES,
            timestamp=datetime(2026, 8, 28, 9, 15),
        ),
        open=Decimal("1040.00"),
        high=Decimal("1050.00"),
        low=Decimal("1038.00"),
        close=Decimal("1047.00"),
        volume=1000,
        source="test",
        fetched_at=datetime(2026, 8, 28, 9, 20),
    )

    first_result = upsert_candle(candle)
    second_result = upsert_candle(candle)

    watermark = get_watermark(
        "NSE:SBIN",
        CandleInterval.FIVE_MINUTES,
    )

    assert first_result == "inserted"
    assert second_result == "unchanged"

    assert watermark is not None
    assert watermark.data_version >= 1