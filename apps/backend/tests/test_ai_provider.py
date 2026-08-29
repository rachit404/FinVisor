from app.ai.fake_provider import FakeAIProvider


def test_fake_ai_provider_generates_response():
    provider = FakeAIProvider()

    response = provider.generate(
        prompt="Analyze NSE:SBIN",
        model="test-model",
    )

    assert "Fake analysis" in response
    assert "test-model" in response
    assert "Analyze NSE:SBIN" in response
    
    
    