import json

from app.domain.market import (
    Candle,
    CandleIdentity,
    CandleInterval,
    MarketDataSnapshot,
)
from app.storage.database import get_connection


def _ensure_snapshot_table(connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS market_data_snapshots (
            snapshot_hash TEXT PRIMARY KEY,
            instrument_id TEXT NOT NULL,
            interval TEXT NOT NULL,
            data_version INTEGER NOT NULL,
            latest_candle_timestamp TEXT,
            candles_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )


def save_snapshot(
    snapshot: MarketDataSnapshot,
) -> None:
    connection = get_connection()

    try:
        _ensure_snapshot_table(connection)

        candles_json = json.dumps(
            [
                {
                    "timestamp": candle.identity.timestamp.isoformat(),
                    "open": str(candle.open),
                    "high": str(candle.high),
                    "low": str(candle.low),
                    "close": str(candle.close),
                    "volume": candle.volume,
                    "source": candle.source,
                    "fetched_at": candle.fetched_at.isoformat(),
                }
                for candle in snapshot.candles
            ],
            sort_keys=True,
            separators=(",", ":"),
        )

        connection.execute(
            """
            INSERT OR IGNORE INTO market_data_snapshots (
                snapshot_hash,
                instrument_id,
                interval,
                data_version,
                latest_candle_timestamp,
                candles_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot.snapshot_hash,
                snapshot.instrument_id,
                snapshot.interval.value,
                snapshot.data_version,
                (
                    snapshot.latest_candle_timestamp.isoformat()
                    if snapshot.latest_candle_timestamp
                    else None
                ),
                candles_json,
                snapshot.latest_candle_timestamp.isoformat()
                if snapshot.latest_candle_timestamp
                else "",
            ),
        )

        connection.commit()

    finally:
        connection.close()


def get_snapshot(
    snapshot_hash: str,
) -> MarketDataSnapshot | None:
    connection = get_connection()

    try:
        _ensure_snapshot_table(connection)

        row = connection.execute(
            """
            SELECT *
            FROM market_data_snapshots
            WHERE snapshot_hash = ?
            """,
            (snapshot_hash,),
        ).fetchone()

        if row is None:
            return None

        candle_data = json.loads(
            row["candles_json"]
        )

        candles = tuple(
            Candle(
                identity=CandleIdentity(
                    instrument_id=row["instrument_id"],
                    interval=CandleInterval(row["interval"]),
                    timestamp=__import__(
                        "datetime"
                    ).datetime.fromisoformat(
                        item["timestamp"]
                    ),
                ),
                open=__import__(
                    "decimal"
                ).Decimal(item["open"]),
                high=__import__(
                    "decimal"
                ).Decimal(item["high"]),
                low=__import__(
                    "decimal"
                ).Decimal(item["low"]),
                close=__import__(
                    "decimal"
                ).Decimal(item["close"]),
                volume=item["volume"],
                source=item["source"],
                fetched_at=__import__(
                    "datetime"
                ).datetime.fromisoformat(
                    item["fetched_at"]
                ),
            )
            for item in candle_data
        )

        from datetime import datetime

        latest_candle_timestamp = (
            datetime.fromisoformat(
                row["latest_candle_timestamp"]
            )
            if row["latest_candle_timestamp"]
            else None
        )

        return MarketDataSnapshot(
            instrument_id=row["instrument_id"],
            interval=CandleInterval(row["interval"]),
            data_version=row["data_version"],
            latest_candle_timestamp=latest_candle_timestamp,
            candles=candles,
            snapshot_hash=row["snapshot_hash"],
        )

    finally:
        connection.close()