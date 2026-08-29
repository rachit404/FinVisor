import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from app.ai.provider import AIProvider
from app.ai.tokenrouter_provider import TokenRouterAIProvider
from app.services.analysis_service import run_analysis


load_dotenv()


app = FastAPI(
    title="FinVisor API",
    version="0.1.0",
)


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
    