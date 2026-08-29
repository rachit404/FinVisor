from datetime import datetime
from decimal import Decimal

from app.domain.market import (
    Candle,
    CandleIdentity,
    CandleInterval,
    MarketDataSnapshot,
)
from app.services.analysis_context import AnalysisContext
from app.services.analysis_prompt import build_analysis_prompt


def test_prompt_contains_snapshot_and_user_question():
    snapshot = MarketDataSnapshot(
        instrument_id="NSE:SBIN",
        interval=CandleInterval.FIVE_MINUTES,
        data_version=7,
        latest_candle_timestamp=datetime(
            2026,
            8,
            28,
            9,
            15,
        ),
        candles=(
            Candle(
                identity=CandleIdentity(
                    instrument_id="NSE:SBIN",
                    interval=CandleInterval.FIVE_MINUTES,
                    timestamp=datetime(
                        2026,
                        8,
                        28,
                        9,
                        15,
                    ),
                ),
                open=Decimal("100"),
                high=Decimal("110"),
                low=Decimal("90"),
                close=Decimal("105"),
                volume=1000,
                source="test",
                fetched_at=datetime(
                    2026,
                    8,
                    28,
                    9,
                    16,
                ),
            ),
        ),
        snapshot_hash="test-prompt-snapshot-001",
    )

    context = AnalysisContext(
        snapshot_hash=snapshot.snapshot_hash,
        instrument_id=snapshot.instrument_id,
        data_version=snapshot.data_version,
        snapshot=snapshot,
    )

    prompt = build_analysis_prompt(
        context,
        "Should I buy this stock?",
    )

    assert "NSE:SBIN" in prompt
    assert "test-prompt-snapshot-001" in prompt
    assert "data_version" in prompt
    assert "Should I buy this stock?" in prompt
    assert '"close": "105"' in prompt


def test_prompt_requires_ai_to_use_only_supplied_market_data():
    snapshot = MarketDataSnapshot(
        instrument_id="NSE:TEST",
        interval=CandleInterval.FIVE_MINUTES,
        data_version=1,
        latest_candle_timestamp=None,
        candles=(),
        snapshot_hash="test-prompt-rules-001",
    )

    context = AnalysisContext(
        snapshot_hash=snapshot.snapshot_hash,
        instrument_id=snapshot.instrument_id,
        data_version=snapshot.data_version,
        snapshot=snapshot,
    )

    prompt = build_analysis_prompt(
        context,
        "Analyze this stock.",
    )

    assert "Use only the market data provided below" in prompt
    assert "Do not invent missing market data" in prompt