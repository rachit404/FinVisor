import json

from app.domain.analysis_response import (
    AnalysisAction,
    StructuredAnalysisResponse,
)


def parse_analysis_response(
    response: str,
) -> StructuredAnalysisResponse:
    data = json.loads(response)

    action = AnalysisAction(data["action"])

    confidence = data["confidence"]

    if not isinstance(confidence, int):
        raise ValueError(
            "confidence must be an integer"
        )

    if confidence < 0 or confidence > 100:
        raise ValueError(
            "confidence must be between 0 and 100"
        )

    summary = data["summary"]

    if not isinstance(summary, str):
        raise ValueError(
            "summary must be a string"
        )

    reasons = data["reasons"]

    if (
        not isinstance(reasons, list)
        or not all(
            isinstance(reason, str)
            for reason in reasons
        )
    ):
        raise ValueError(
            "reasons must be a list of strings"
        )

    return StructuredAnalysisResponse(
        action=action,
        confidence=confidence,
        summary=summary,
        reasons=tuple(reasons),
    )