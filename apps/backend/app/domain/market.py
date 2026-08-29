from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class CandleInterval(StrEnum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"


@dataclass(frozen=True)
class Instrument:
    instrument_id: str
    symbol: str
    exchange: str
    name: str


@dataclass(frozen=True)
class CandleIdentity:
    instrument_id: str
    interval: CandleInterval
    timestamp: datetime


@dataclass
class Candle:
    identity: CandleIdentity

    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

    volume: int | None

    source: str
    fetched_at: datetime


@dataclass(frozen=True)
class MarketDataWatermark:
    instrument_id: str
    interval: CandleInterval

    latest_candle_timestamp: datetime | None

    data_version: int
    
@dataclass(frozen=True)
class MarketSyncResult:
    inserted: int
    updated: int
    unchanged: int

    previous_data_version: int
    current_data_version: int

    new_data_available: bool
    
@dataclass(frozen=True)
class MarketDataSnapshot:
    instrument_id: str
    interval: CandleInterval

    data_version: int
    latest_candle_timestamp: datetime | None

    candles: tuple[Candle, ...]

    snapshot_hash: str