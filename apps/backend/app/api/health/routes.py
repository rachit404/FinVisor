from flask import Blueprint, jsonify

from app.providers.llm.tokenrouter import TokenRouterProvider


health_bp = Blueprint("health", __name__)


@health_bp.get("")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "finvisor-backend",
        }
    )


@health_bp.get("/models")
def models():
    provider = TokenRouterProvider()

    return jsonify(
        {
            "models": provider.list_models(),
        }
    )
    
@health_bp.get("/llm-test")
def llm_test():
    provider = TokenRouterProvider()

    response = provider.chat(
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: TokenRouter connection successful",
            }
        ],
        model="qwen/qwen3.8-max-free",
    )

    return jsonify(
        {
            "status": "ok",
            "model": "qwen/qwen3.8-max-free",
            "response": response,
        }
    )