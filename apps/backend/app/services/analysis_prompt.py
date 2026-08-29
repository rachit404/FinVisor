import json

from app.services.analysis_context import AnalysisContext


def build_analysis_prompt(
    context: AnalysisContext,
    user_prompt: str,
) -> str:
    snapshot = context.snapshot

    market_data = {
        "instrument_id": snapshot.instrument_id,
        "interval": snapshot.interval.value,
        "data_version": snapshot.data_version,
        "snapshot_hash": snapshot.snapshot_hash,
        "latest_candle_timestamp": (
            snapshot.latest_candle_timestamp.isoformat()
            if snapshot.latest_candle_timestamp
            else None
        ),
        "candles": [
            {
                "timestamp": candle.identity.timestamp.isoformat(),
                "open": str(candle.open),
                "high": str(candle.high),
                "low": str(candle.low),
                "close": str(candle.close),
                "volume": candle.volume,
            }
            for candle in snapshot.candles
        ],
    }

    market_data_json = json.dumps(
        market_data,
        indent=2,
        sort_keys=True,
    )

    return f"""You are FinVisor, an AI assistant for stock analysis.

Use only the market data provided below for factual claims about
price, candles, and market movement.

Do not invent missing market data.
If the available data is insufficient, clearly say so.

MARKET DATA:
{market_data_json}

USER QUESTION:
{user_prompt}
"""