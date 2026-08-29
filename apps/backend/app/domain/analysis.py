from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AnalysisRecord:
    analysis_id: str
    snapshot_hash: str
    instrument_id: str
    data_version: int

    prompt: str
    response: str

    model: str
    created_at: datetime
    
    