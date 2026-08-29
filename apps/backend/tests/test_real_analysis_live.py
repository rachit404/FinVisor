import os

from dotenv import load_dotenv

from app.ai.tokenrouter_provider import TokenRouterAIProvider
from app.domain.market import CandleInterval
from app.services.analysis_service import run_analysis
from app.storage.analysis_repository import get_latest_snapshot


load_dotenv()


def main():
    snapshot = get_latest_snapshot(
        instrument_id="NSE:SBIN",
        interval=CandleInterval.FIVE_MINUTES,
    )

    if snapshot is None:
        raise RuntimeError(
            "No saved market snapshot found. "
            "Create and save a snapshot first."
        )

    api_key = os.environ.get(
        "TOKENROUTER_API_KEY"
    )

    base_url = os.environ.get(
        "TOKENROUTER_BASE_URL"
    )

    model = os.environ.get(
        "TOKENROUTER_MODEL"
    )

    if not api_key or not base_url or not model:
        raise RuntimeError(
            "TokenRouter configuration is incomplete."
        )

    provider = TokenRouterAIProvider(
        api_key=api_key,
        base_url=base_url,
    )

    result = run_analysis(
        snapshot_hash=snapshot.snapshot_hash,
        prompt=(
            "Analyze the available market data. "
            "Give a conservative trading assessment."
        ),
        model=model,
        provider=provider,
    )

    if result is None:
        raise RuntimeError(
            "Analysis could not be created."
        )

    print("\n=== FINVISOR REAL ANALYSIS ===\n")

    print(
        f"Instrument: "
        f"{result.analysis.instrument_id}"
    )

    print(
        f"Data version: "
        f"{result.analysis.data_version}"
    )

    print(
        f"Analysis ID: "
        f"{result.analysis.analysis_id}"
    )

    print("\nAction:")
    print(result.structured_response.action.value)

    print("\nConfidence:")
    print(result.structured_response.confidence)

    print("\nSummary:")
    print(result.structured_response.summary)

    print("\nReasons:")

    for reason in result.structured_response.reasons:
        print(f"- {reason}")


if __name__ == "__main__":
    main()