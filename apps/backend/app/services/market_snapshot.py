import hashlib
import json

from app.domain.market import (
    CandleInterval,
    MarketDataSnapshot,
)

from app.storage.market_repository import (
    get_candles,
    get_watermark,
)


def create_market_snapshot(
    instrument_id: str,
    interval: CandleInterval,
) -> MarketDataSnapshot:
    candles = get_candles(
        instrument_id,
        interval,
    )

    watermark = get_watermark(
        instrument_id,
        interval,
    )

    data_version = (
        watermark.data_version
        if watermark is not None
        else 0
    )

    latest_candle_timestamp = (
        watermark.latest_candle_timestamp
        if watermark is not None
        else None
    )

    hash_payload = [
        {
            "timestamp": candle.identity.timestamp.isoformat(),
            "open": str(candle.open),
            "high": str(candle.high),
            "low": str(candle.low),
            "close": str(candle.close),
            "volume": candle.volume,
        }
        for candle in candles
    ]

    serialized = json.dumps(
        hash_payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    snapshot_hash = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

    return MarketDataSnapshot(
        instrument_id=instrument_id,
        interval=interval,
        data_version=data_version,
        latest_candle_timestamp=latest_candle_timestamp,
        candles=tuple(candles),
        snapshot_hash=snapshot_hash,
    )