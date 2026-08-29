import json
import re

from app.domain.analysis_response import (
    AnalysisAction,
    StructuredAnalysisResponse,
)


def _extract_json(
    response: str,
) -> str:
    cleaned = response.strip()

    if not cleaned:
        raise ValueError(
            "AI provider returned an empty response"
        )

    markdown_match = re.search(
        r"```(?:json)?\s*(.*?)\s*```",
        cleaned,
        re.DOTALL | re.IGNORECASE,
    )

    if markdown_match:
        return markdown_match.group(1).strip()

    if cleaned.startswith("{") and cleaned.endswith("}"):
        return cleaned

    json_start = cleaned.find("{")
    json_end = cleaned.rfind("}")

    if (
        json_start != -1
        and json_end != -1
        and json_end > json_start
    ):
        return cleaned[
            json_start : json_end + 1
        ]

    raise ValueError(
        "AI provider response does not contain valid JSON"
    )


def parse_analysis_response(
    response: str,
) -> StructuredAnalysisResponse:
    json_response = _extract_json(response)

    try:
        data = json.loads(json_response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "AI provider returned invalid JSON: "
            f"{exc.msg}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "AI response must be a JSON object"
        )

    required_fields = {
        "action",
        "confidence",
        "summary",
        "reasons",
    }

    missing_fields = (
        required_fields - data.keys()
    )

    if missing_fields:
        raise ValueError(
            "AI response is missing required fields: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    try:
        action = AnalysisAction(
            data["action"]
        )
    except ValueError as exc:
        raise ValueError(
            "action must be one of: "
            "buy, sell, hold"
        ) from exc

    confidence = data["confidence"]

    if (
        not isinstance(confidence, int)
        or isinstance(confidence, bool)
    ):
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
    
    