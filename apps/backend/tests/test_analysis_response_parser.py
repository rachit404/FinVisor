import pytest

from app.domain.analysis_response import (
    AnalysisAction,
)
from app.services.analysis_response_parser import (
    parse_analysis_response,
)


def test_parse_valid_analysis_response():
    response = """
    {
        "action": "buy",
        "confidence": 72,
        "summary": "Price shows positive momentum.",
        "reasons": [
            "Recent candles closed higher.",
            "Volume remained stable."
        ]
    }
    """

    result = parse_analysis_response(response)

    assert result.action == AnalysisAction.BUY
    assert result.confidence == 72
    assert result.summary == (
        "Price shows positive momentum."
    )
    assert result.reasons == (
        "Recent candles closed higher.",
        "Volume remained stable.",
    )


def test_invalid_confidence_raises_error():
    response = """
    {
        "action": "buy",
        "confidence": 150,
        "summary": "Test",
        "reasons": []
    }
    """

    with pytest.raises(ValueError):
        parse_analysis_response(response)


def test_invalid_action_raises_error():
    response = """
    {
        "action": "strong_buy",
        "confidence": 50,
        "summary": "Test",
        "reasons": []
    }
    """

    with pytest.raises(ValueError):
        parse_analysis_response(response)