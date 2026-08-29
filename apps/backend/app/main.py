import os
from typing import Annotated, Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from app.ai.provider import AIProvider
from app.ai.tokenrouter_provider import TokenRouterAIProvider
from app.domain.market import CandleInterval
from app.services.analysis_service import run_analysis
from app.storage.market_snapshot_repository import get_latest_snapshot


load_dotenv()


app = FastAPI(
    title="FinVisor API",
    version="0.1.0",
)


class StockContextRequest(BaseModel):
    platform: str
    symbol: str

    exchange: str | None = None
    companyName: str | None = None

    instrument: dict[str, Any] | None = None

    price: float | None = None
    change: float | None = None
    changePercent: float | None = None

    url: str
    capturedAt: str


class AnalysisRequest(BaseModel):
    snapshot_hash: str
    prompt: str
    model: str | None = None


class AnalysisResponse(BaseModel):
    analysis_id: str
    snapshot_hash: str
    instrument_id: str
    data_version: int

    action: str
    confidence: int
    summary: str
    reasons: list[str]


class SnapshotResponse(BaseModel):
    snapshot_hash: str
    instrument_id: str
    interval: str
    data_version: int
    latest_candle_timestamp: str | None
    candle_count: int


def get_ai_provider() -> AIProvider:
    api_key = os.environ.get(
        "TOKENROUTER_API_KEY"
    )

    base_url = os.environ.get(
        "TOKENROUTER_BASE_URL"
    )

    if not api_key or not base_url:
        raise HTTPException(
            status_code=500,
            detail="TokenRouter is not configured",
        )

    return TokenRouterAIProvider(
        api_key=api_key,
        base_url=base_url,
    )


@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }


@app.post("/api/context")
def receive_stock_context(
    context: StockContextRequest,
):
    print(
        "[FinVisor] Stock context received:",
        context.model_dump(),
    )

    return {
        "success": True,
        "message": "Stock context received",
        "symbol": context.symbol,
        "platform": context.platform,
    }


@app.get(
    "/snapshots/latest",
    response_model=SnapshotResponse,
)
def get_latest_market_snapshot(
    instrument_id: str,
    interval: CandleInterval,
):
    snapshot = get_latest_snapshot(
        instrument_id=instrument_id,
        interval=interval,
    )

    if snapshot is None:
        raise HTTPException(
            status_code=404,
            detail="Market snapshot not found",
        )

    return SnapshotResponse(
        snapshot_hash=snapshot.snapshot_hash,
        instrument_id=snapshot.instrument_id,
        interval=snapshot.interval.value,
        data_version=snapshot.data_version,
        latest_candle_timestamp=(
            snapshot.latest_candle_timestamp.isoformat()
            if snapshot.latest_candle_timestamp is not None
            else None
        ),
        candle_count=len(snapshot.candles),
    )


@app.post(
    "/analysis",
    response_model=AnalysisResponse,
)
def create_analysis(
    request: AnalysisRequest,
    provider: Annotated[
        AIProvider,
        Depends(get_ai_provider),
    ],
):
    model = (
        request.model
        or os.environ.get("TOKENROUTER_MODEL")
    )

    if not model:
        raise HTTPException(
            status_code=500,
            detail="TokenRouter model is not configured",
        )

    result = run_analysis(
        snapshot_hash=request.snapshot_hash,
        prompt=request.prompt,
        model=model,
        provider=provider,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Market snapshot not found",
        )

    structured = result.structured_response

    return AnalysisResponse(
        analysis_id=result.analysis.analysis_id,
        snapshot_hash=result.analysis.snapshot_hash,
        instrument_id=result.analysis.instrument_id,
        data_version=result.analysis.data_version,
        action=structured.action.value,
        confidence=structured.confidence,
        summary=structured.summary,
        reasons=list(structured.reasons),
    )
    