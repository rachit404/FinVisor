from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.ai.provider import AIProvider
from app.domain.analysis import AnalysisRecord
from app.domain.analysis_response import StructuredAnalysisResponse
from app.services.analysis_context import load_analysis_context
from app.services.analysis_prompt import build_analysis_prompt
from app.services.analysis_response_parser import (
    parse_analysis_response,
)
from app.storage.analysis_repository import save_analysis


@dataclass(frozen=True)
class AnalysisResult:
    analysis: AnalysisRecord
    structured_response: StructuredAnalysisResponse


def run_analysis(
    *,
    snapshot_hash: str,
    prompt: str,
    model: str,
    provider: AIProvider,
) -> AnalysisResult | None:
    context = load_analysis_context(snapshot_hash)

    if context is None:
        return None

    analysis_prompt = build_analysis_prompt(
        context,
        prompt,
    )

    response = provider.generate(
        prompt=analysis_prompt,
        model=model,
    )

    structured_response = parse_analysis_response(
        response
    )

    analysis = AnalysisRecord(
        analysis_id=str(uuid4()),
        snapshot_hash=context.snapshot_hash,
        instrument_id=context.instrument_id,
        data_version=context.data_version,
        prompt=prompt,
        response=response,
        model=model,
        created_at=datetime.now(timezone.utc),
    )

    save_analysis(analysis)

    return AnalysisResult(
        analysis=analysis,
        structured_response=structured_response,
    )
    
    