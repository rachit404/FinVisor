import json
import os
import time
from urllib import error, request

from dotenv import load_dotenv


load_dotenv()

API_KEY = os.environ.get("TOKENROUTER_API_KEY")
BASE_URL = os.environ.get("TOKENROUTER_BASE_URL")

MODELS_TO_TEST = [
    "qwen/qwen3.8-max-free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "deepseek/deepseek-v4-pro-0813-free",
    "z-ai/glm-5.3-free",
]


def api_request(
    endpoint: str,
    method: str = "GET",
    payload: dict | None = None,
):
    if not API_KEY:
        raise RuntimeError(
            "TOKENROUTER_API_KEY is missing"
        )

    if not BASE_URL:
        raise RuntimeError(
            "TOKENROUTER_BASE_URL is missing"
        )

    url = (
        f"{BASE_URL.rstrip('/')}"
        f"{endpoint}"
    )

    data = (
        json.dumps(payload).encode("utf-8")
        if payload is not None
        else None
    )

    http_request = request.Request(
        url,
        data=data,
        headers={
            "Authorization": (
                f"Bearer {API_KEY}"
            ),
            "Content-Type": "application/json",
        },
        method=method,
    )

    try:
        with request.urlopen(
            http_request,
            timeout=60,
        ) as response:
            body = response.read().decode(
                "utf-8"
            )

            return (
                response.status,
                json.loads(body),
                None,
            )

    except error.HTTPError as exc:
        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        return (
            exc.code,
            None,
            body,
        )

    except Exception as exc:
        return (
            None,
            None,
            str(exc),
        )


def get_available_models() -> set[str]:
    print(
        "\n=== Checking available models ==="
    )

    status, data, error_message = api_request(
        "/models"
    )

    if status != 200 or data is None:
        raise RuntimeError(
            "Could not retrieve models: "
            f"{error_message}"
        )

    models = {
        item["id"]
        for item in data.get("data", [])
        if "id" in item
    }

    print(f"Status: {status}")
    print(
        f"Models found: {len(models)}"
    )

    for model in sorted(models):
        print(f"  - {model}")

    return models


def test_model(model: str) -> dict:
    print("\n" + "=" * 60)
    print(f"Testing model: {model}")
    print("=" * 60)

    start_time = time.perf_counter()

    status, data, error_message = api_request(
        "/chat/completions",
        method="POST",
        payload={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Reply with exactly these three words: "
                        "TokenRouter test successful"
                    ),
                }
            ],
        },
    )

    elapsed = (
        time.perf_counter()
        - start_time
    )

    result = {
        "model": model,
        "status": status,
        "success": False,
        "latency_seconds": round(
            elapsed,
            2,
        ),
        "response": None,
        "error": error_message,
    }

    if (
        status == 200
        and data is not None
    ):
        try:
            content = (
                data["choices"][0]
                ["message"]
                ["content"]
            )

            result["success"] = True
            result["response"] = content

            print("Result: SUCCESS")
            print(
                f"Latency: {elapsed:.2f}s"
            )
            print(
                f"Response: {content}"
            )

        except (
            KeyError,
            IndexError,
            TypeError,
        ):
            result["error"] = (
                "Unexpected API response format: "
                + json.dumps(data)
            )

            print("Result: FAILED")
            print(
                "Reason: Unexpected response format"
            )

    else:
        print("Result: FAILED")
        print(f"HTTP Status: {status}")
        print(
            f"Latency: {elapsed:.2f}s"
        )

        if error_message:
            print(
                f"Error: {error_message}"
            )

    return result


def print_summary(results: list[dict]) -> None:
    print("\n")
    print("=" * 75)
    print("TOKENROUTER MODEL TEST SUMMARY")
    print("=" * 75)

    for result in results:
        status = (
            "SUCCESS"
            if result["success"]
            else "FAILED"
        )

        print(
            f"\nModel: {result['model']}"
        )
        print(f"Result: {status}")
        print(
            f"HTTP Status: {result['status']}"
        )
        print(
            "Latency: "
            f"{result['latency_seconds']}s"
        )

        if result["response"]:
            print(
                f"Response: {result['response']}"
            )

        if result["error"]:
            print(
                f"Error: {result['error']}"
            )

    successful_models = [
        result["model"]
        for result in results
        if result["success"]
    ]

    print("\n" + "=" * 75)
    print(
        "WORKING MODELS: "
        f"{len(successful_models)}"
    )

    for model in successful_models:
        print(f"  - {model}")

    print("=" * 75)


def main():
    print(
        "=== FinVisor TokenRouter Model Test ==="
    )

    print(
        f"Base URL: {BASE_URL}"
    )

    print(
        "API key present: "
        f"{bool(API_KEY)}"
    )

    available_models = (
        get_available_models()
    )

    results: list[dict] = []

    for model in MODELS_TO_TEST:
        if model not in available_models:
            print(
                "\nSkipping unavailable catalog model: "
                f"{model}"
            )

            results.append(
                {
                    "model": model,
                    "status": None,
                    "success": False,
                    "latency_seconds": 0,
                    "response": None,
                    "error": (
                        "Model not present "
                        "in /models response"
                    ),
                }
            )

            continue

        results.append(
            test_model(model)
        )

    print_summary(results)


if __name__ == "__main__":
    main()