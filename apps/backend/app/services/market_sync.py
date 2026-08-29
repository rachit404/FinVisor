from app.domain.market import (
    Candle,
    CandleInterval,
    MarketSyncResult,
)
from app.services.market_snapshot import (
    create_market_snapshot,
)
from app.storage.market_repository import (
    get_watermark,
    upsert_candle,
)
from app.storage.market_snapshot_repository import (
    save_snapshot,
)


def sync_candles(
    instrument_id: str,
    interval: CandleInterval,
    candles: list[Candle],
) -> MarketSyncResult:
    previous_watermark = get_watermark(
        instrument_id,
        interval,
    )

    previous_data_version = (
        previous_watermark.data_version
        if previous_watermark is not None
        else 0
    )

    inserted = 0
    updated = 0
    unchanged = 0

    sorted_candles = sorted(
        candles,
        key=lambda candle: candle.identity.timestamp,
    )

    for candle in sorted_candles:
        result = upsert_candle(candle)

        if result == "inserted":
            inserted += 1
        elif result == "updated":
            updated += 1
        else:
            unchanged += 1

    current_watermark = get_watermark(
        instrument_id,
        interval,
    )

    current_data_version = (
        current_watermark.data_version
        if current_watermark is not None
        else previous_data_version
    )

    new_data_available = inserted > 0 or updated > 0

    if new_data_available:
        snapshot = create_market_snapshot(
            instrument_id,
            interval,
        )

        save_snapshot(snapshot)

    return MarketSyncResult(
        inserted=inserted,
        updated=updated,
        unchanged=unchanged,
        previous_data_version=previous_data_version,
        current_data_version=current_data_version,
        new_data_available=new_data_available,
    )
    
    
    
    