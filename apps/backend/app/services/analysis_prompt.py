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

Analyze the market data provided below and answer the user's question.

IMPORTANT RULES:

1. Use only the provided market data for factual claims about
   prices, candles, volume, and market movement.

2. Do not invent missing market data.

3. Do not claim to know future prices or guarantee future outcomes.

4. If the available data is insufficient, use "hold" and explain
   the limitation in the summary or reasons.

5. Return ONLY valid JSON.

6. Do not use Markdown.

7. Do not wrap the JSON in triple backticks.

8. Do not include any text before or after the JSON.

Your response MUST use exactly this structure:

{{
  "action": "buy",
  "confidence": 0,
  "summary": "Brief analysis summary.",
  "reasons": [
    "Reason 1",
    "Reason 2"
  ]
}}

VALID ACTION VALUES:

- "buy"
- "sell"
- "hold"

CONFIDENCE RULES:

- Must be an integer.
- Must be between 0 and 100.

MARKET DATA:
{market_data_json}

USER QUESTION:
{user_prompt}
"""