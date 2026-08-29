from datetime import datetime
from decimal import Decimal

from app.ai.fake_provider import FakeAIProvider
from app.domain.analysis_response import AnalysisAction
from app.domain.market import (
    Candle,
    CandleIdentity,
    CandleInterval,
    MarketDataSnapshot,
)
from app.services.analysis_service import run_analysis
from app.storage.analysis_repository import get_analysis
from app.storage.database import initialize_database
from app.storage.market_snapshot_repository import save_snapshot


class StructuredFakeAIProvider(FakeAIProvider):
    def generate(
        self,
        *,
        prompt: str,
        model: str,
    ) -> str:
        return """
        {
            "action": "buy",
            "confidence": 72,
            "summary": "Positive short-term momentum.",
            "reasons": [
                "Recent candle closed higher.",
                "Price remains above the opening level."
            ]
        }
        """


def create_snapshot() -> MarketDataSnapshot:
    return MarketDataSnapshot(
        instrument_id="TEST:NSE:SBIN:AI",
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
                    instrument_id="TEST:NSE:SBIN:AI",
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
        snapshot_hash="test-ai-snapshot-provider-001",
    )


def test_run_analysis_uses_structured_response():
    initialize_database()

    snapshot = create_snapshot()
    save_snapshot(snapshot)

    provider = StructuredFakeAIProvider()

    result = run_analysis(
        snapshot_hash=snapshot.snapshot_hash,
        prompt="Analyze this stock.",
        model="test-model",
        provider=provider,
    )

    assert result is not None

    analysis = result.analysis
    structured = result.structured_response

    assert analysis.snapshot_hash == snapshot.snapshot_hash
    assert analysis.instrument_id == snapshot.instrument_id
    assert analysis.data_version == 7

    assert structured.action == AnalysisAction.BUY
    assert structured.confidence == 72
    assert structured.summary == (
        "Positive short-term momentum."
    )

    restored = get_analysis(
        analysis.analysis_id
    )

    assert restored == analysis


def test_run_analysis_returns_none_for_missing_snapshot():
    initialize_database()

    provider = StructuredFakeAIProvider()

    result = run_analysis(
        snapshot_hash="missing-snapshot",
        prompt="Analyze this stock.",
        model="test-model",
        provider=provider,
    )

    assert result is None
    
    