import json
from urllib import request


class TokenRouterAIProvider:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def generate(
        self,
        *,
        prompt: str,
        model: str,
    ) -> str:
        payload = json.dumps(
            {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            }
        ).encode("utf-8")

        http_request = request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Authorization": (
                    f"Bearer {self.api_key}"
                ),
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with request.urlopen(http_request) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        return data["choices"][0]["message"]["content"]