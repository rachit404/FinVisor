import json
from unittest.mock import MagicMock, patch

from app.ai.tokenrouter_provider import (
    TokenRouterAIProvider,
)


def test_tokenrouter_provider_generates_response():
    provider = TokenRouterAIProvider(
        api_key="test-api-key",
        base_url="https://example.com/v1",
    )

    mock_response = MagicMock()

    mock_response.read.return_value = json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "content": "AI response",
                    }
                }
            ]
        }
    ).encode("utf-8")

    mock_response.__enter__.return_value = mock_response

    with patch(
        "app.ai.tokenrouter_provider.request.urlopen",
        return_value=mock_response,
    ):
        response = provider.generate(
            prompt="Analyze this stock.",
            model="test-model",
        )

    assert response == "AI response"