from dataclasses import dataclass
from enum import Enum


class AnalysisAction(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass(frozen=True)
class StructuredAnalysisResponse:
    action: AnalysisAction
    confidence: int
    summary: str
    reasons: tuple[str, ...]