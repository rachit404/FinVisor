from pathlib import Path
import sqlite3


BACKEND_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BACKEND_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "finvisor.db"


def get_connection() -> sqlite3.Connection:
    DATABASE_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    connection = get_connection()

    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS market_candles (
                instrument_id TEXT NOT NULL,
                interval TEXT NOT NULL,
                candle_timestamp TEXT NOT NULL,

                open TEXT NOT NULL,
                high TEXT NOT NULL,
                low TEXT NOT NULL,
                close TEXT NOT NULL,

                volume INTEGER,

                source TEXT NOT NULL,
                fetched_at TEXT NOT NULL,

                PRIMARY KEY (
                    instrument_id,
                    interval,
                    candle_timestamp
                )
            );

            CREATE TABLE IF NOT EXISTS market_data_watermarks (
                instrument_id TEXT NOT NULL,
                interval TEXT NOT NULL,

                latest_candle_timestamp TEXT,
                data_version INTEGER NOT NULL DEFAULT 0,

                PRIMARY KEY (
                    instrument_id,
                    interval
                )
            );
            """
        )

        connection.commit()

    finally:
        connection.close()