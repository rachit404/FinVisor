from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.domain.analysis import AnalysisRecord
from app.services.analysis_context import load_analysis_context
from app.storage.analysis_repository import save_analysis


@dataclass(frozen=True)
class AnalysisResult:
    analysis: AnalysisRecord


def run_analysis(
    snapshot_hash: str,
    prompt: str,
    model: str,
    response: str,
) -> AnalysisResult | None:
    context = load_analysis_context(snapshot_hash)

    if context is None:
        return None

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
    )