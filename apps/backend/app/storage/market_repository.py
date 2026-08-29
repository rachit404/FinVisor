from datetime import datetime
from decimal import Decimal

from app.domain.market import (
    Candle,
    CandleInterval,
    CandleIdentity,
    MarketDataWatermark,
)

from app.storage.database import get_connection


def _serialize_datetime(value: datetime) -> str:
    return value.isoformat()


def _deserialize_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def upsert_candle(candle: Candle) -> str:
    connection = get_connection()

    try:
        existing = connection.execute(
            """
            SELECT
                open,
                high,
                low,
                close,
                volume
            FROM market_candles
            WHERE
                instrument_id = ?
                AND interval = ?
                AND candle_timestamp = ?
            """,
            (
                candle.identity.instrument_id,
                candle.identity.interval.value,
                _serialize_datetime(candle.identity.timestamp),
            ),
        ).fetchone()

        values = (
            str(candle.open),
            str(candle.high),
            str(candle.low),
            str(candle.close),
            candle.volume,
        )

        if existing is None:
            connection.execute(
                """
                INSERT INTO market_candles (
                    instrument_id,
                    interval,
                    candle_timestamp,
                    open,
                    high,
                    low,
                    close,
                    volume,
                    source,
                    fetched_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candle.identity.instrument_id,
                    candle.identity.interval.value,
                    _serialize_datetime(candle.identity.timestamp),
                    *values,
                    candle.source,
                    _serialize_datetime(candle.fetched_at),
                ),
            )

            _update_watermark(
                connection,
                candle.identity.instrument_id,
                candle.identity.interval,
                candle.identity.timestamp,
            )

            connection.commit()

            return "inserted"

        existing_values = (
            existing["open"],
            existing["high"],
            existing["low"],
            existing["close"],
            existing["volume"],
        )

        if existing_values == values:
            return "unchanged"

        connection.execute(
            """
            UPDATE market_candles
            SET
                open = ?,
                high = ?,
                low = ?,
                close = ?,
                volume = ?,
                source = ?,
                fetched_at = ?
            WHERE
                instrument_id = ?
                AND interval = ?
                AND candle_timestamp = ?
            """,
            (
                *values,
                candle.source,
                _serialize_datetime(candle.fetched_at),
                candle.identity.instrument_id,
                candle.identity.interval.value,
                _serialize_datetime(candle.identity.timestamp),
            ),
        )

        _update_watermark(
            connection,
            candle.identity.instrument_id,
            candle.identity.interval,
            candle.identity.timestamp,
        )

        connection.commit()

        return "updated"

    finally:
        connection.close()


def _update_watermark(
    connection,
    instrument_id: str,
    interval: CandleInterval,
    candle_timestamp: datetime,
) -> None:
    existing = connection.execute(
        """
        SELECT
            latest_candle_timestamp,
            data_version
        FROM market_data_watermarks
        WHERE
            instrument_id = ?
            AND interval = ?
        """,
        (
            instrument_id,
            interval.value,
        ),
    ).fetchone()

    if existing is None:
        connection.execute(
            """
            INSERT INTO market_data_watermarks (
                instrument_id,
                interval,
                latest_candle_timestamp,
                data_version
            )
            VALUES (?, ?, ?, 1)
            """,
            (
                instrument_id,
                interval.value,
                _serialize_datetime(candle_timestamp),
            ),
        )

        return

    existing_timestamp = (
        _deserialize_datetime(existing["latest_candle_timestamp"])
        if existing["latest_candle_timestamp"]
        else None
    )

    latest_timestamp = candle_timestamp

    if (
        existing_timestamp is not None
        and existing_timestamp > candle_timestamp
    ):
        latest_timestamp = existing_timestamp

    connection.execute(
        """
        UPDATE market_data_watermarks
        SET
            latest_candle_timestamp = ?,
            data_version = data_version + 1
        WHERE
            instrument_id = ?
            AND interval = ?
        """,
        (
            _serialize_datetime(latest_timestamp),
            instrument_id,
            interval.value,
        ),
    )


def get_watermark(
    instrument_id: str,
    interval: CandleInterval,
) -> MarketDataWatermark | None:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                instrument_id,
                interval,
                latest_candle_timestamp,
                data_version
            FROM market_data_watermarks
            WHERE
                instrument_id = ?
                AND interval = ?
            """,
            (
                instrument_id,
                interval.value,
            ),
        ).fetchone()

        if row is None:
            return None

        latest_timestamp = (
            _deserialize_datetime(row["latest_candle_timestamp"])
            if row["latest_candle_timestamp"]
            else None
        )

        return MarketDataWatermark(
            instrument_id=row["instrument_id"],
            interval=CandleInterval(row["interval"]),
            latest_candle_timestamp=latest_timestamp,
            data_version=row["data_version"],
        )

    finally:
        connection.close()


def get_candle(
    identity: CandleIdentity,
) -> Candle | None:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM market_candles
            WHERE
                instrument_id = ?
                AND interval = ?
                AND candle_timestamp = ?
            """,
            (
                identity.instrument_id,
                identity.interval.value,
                _serialize_datetime(identity.timestamp),
            ),
        ).fetchone()

        if row is None:
            return None

        return Candle(
            identity=identity,
            open=Decimal(row["open"]),
            high=Decimal(row["high"]),
            low=Decimal(row["low"]),
            close=Decimal(row["close"]),
            volume=row["volume"],
            source=row["source"],
            fetched_at=_deserialize_datetime(row["fetched_at"]),
        )

    finally:
        connection.close()


def get_candles(
    instrument_id: str,
    interval: CandleInterval,
) -> list[Candle]:
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM market_candles
            WHERE
                instrument_id = ?
                AND interval = ?
            ORDER BY candle_timestamp ASC
            """,
            (
                instrument_id,
                interval.value,
            ),
        ).fetchall()

        candles: list[Candle] = []

        for row in rows:
            candles.append(
                Candle(
                    identity=CandleIdentity(
                        instrument_id=row["instrument_id"],
                        interval=CandleInterval(row["interval"]),
                        timestamp=_deserialize_datetime(
                            row["candle_timestamp"]
                        ),
                    ),
                    open=Decimal(row["open"]),
                    high=Decimal(row["high"]),
                    low=Decimal(row["low"]),
                    close=Decimal(row["close"]),
                    volume=row["volume"],
                    source=row["source"],
                    fetched_at=_deserialize_datetime(
                        row["fetched_at"]
                    ),
                )
            )

        return candles

    finally:
        connection.close()
        
        