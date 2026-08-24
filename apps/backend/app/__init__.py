from flask import Flask

from app.api.health.routes import health_bp
from app.config.settings import settings


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["DEBUG"] = settings.FLASK_DEBUG

    app.register_blueprint(
        health_bp,
        url_prefix="/api/health",
    )

    return app