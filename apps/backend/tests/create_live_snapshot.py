from datetime import datetime, timedelta
from decimal import Decimal

from app.domain.market import (
    Candle,
    CandleIdentity,
    CandleInterval,
)
from app.services.market_sync import sync_candles
from app.storage.database import initialize_database


INSTRUMENT_ID = "NSE:SBIN"
INTERVAL = CandleInterval.FIVE_MINUTES


def create_candle(
    timestamp: datetime,
    open_price: str,
    high_price: str,
    low_price: str,
    close_price: str,
    volume: int,
) -> Candle:
    return Candle(
        identity=CandleIdentity(
            instrument_id=INSTRUMENT_ID,
            interval=INTERVAL,
            timestamp=timestamp,
        ),
        open=Decimal(open_price),
        high=Decimal(high_price),
        low=Decimal(low_price),
        close=Decimal(close_price),
        volume=volume,
        source="live-test",
        fetched_at=datetime.now(),
    )


def main():
    initialize_database()

    start = datetime(2026, 8, 28, 9, 15)

    candles = [
        create_candle(
            start + timedelta(minutes=index * 5),
            str(100 + index),
            str(102 + index),
            str(99 + index),
            str(101 + index),
            100000 + index * 5000,
        )
        for index in range(10)
    ]

    result = sync_candles(
        instrument_id=INSTRUMENT_ID,
        interval=INTERVAL,
        candles=candles,
    )

    print("\n=== FINVISOR LIVE SNAPSHOT CREATED ===")
    print(f"Instrument: {INSTRUMENT_ID}")
    print(f"Interval: {INTERVAL.value}")
    print(f"Inserted: {result.inserted}")
    print(f"Updated: {result.updated}")
    print(f"Unchanged: {result.unchanged}")
    print(f"Previous data version: {result.previous_data_version}")
    print(f"Current data version: {result.current_data_version}")
    print(f"New data available: {result.new_data_available}")


if __name__ == "__main__":
    main()