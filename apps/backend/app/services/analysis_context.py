from dataclasses import dataclass

from app.domain.market import MarketDataSnapshot
from app.storage.market_snapshot_repository import (
    get_snapshot,
)


@dataclass(frozen=True)
class AnalysisContext:
    snapshot_hash: str
    instrument_id: str
    data_version: int
    snapshot: MarketDataSnapshot


def load_analysis_context(
    snapshot_hash: str,
) -> AnalysisContext | None:
    snapshot = get_snapshot(snapshot_hash)

    if snapshot is None:
        return None

    return AnalysisContext(
        snapshot_hash=snapshot.snapshot_hash,
        instrument_id=snapshot.instrument_id,
        data_version=snapshot.data_version,
        snapshot=snapshot,
    )
    
    
    