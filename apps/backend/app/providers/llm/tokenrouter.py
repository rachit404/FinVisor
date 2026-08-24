from typing import Any

from openai import OpenAI

from app.config.settings import settings
from app.providers.llm.base import LLMProvider


class TokenRouterProvider(LLMProvider):

    def __init__(self) -> None:
        if not settings.TOKENROUTER_API_KEY:
            raise RuntimeError(
                "TOKENROUTER_API_KEY is not configured"
            )

        self.client = OpenAI(
            base_url=settings.TOKENROUTER_BASE_URL,
            api_key=settings.TOKENROUTER_API_KEY,
        )

    def list_models(self) -> list[dict[str, Any]]:
        response = self.client.models.list()

        return [
            {
                "id": model.id,
                "object": getattr(model, "object", None),
            }
            for model in response.data
        ]

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
    ) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
        )

        return response.choices[0].message.content or ""