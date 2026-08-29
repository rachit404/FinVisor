from flask import Blueprint, jsonify, request

context_bp = Blueprint("context", __name__, url_prefix="/api/context")


@context_bp.post("")
def receive_context():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "Request body is required"
        }), 400

    return jsonify({
        "success": True,
        "message": "Stock context received",
        "context": data,
    })