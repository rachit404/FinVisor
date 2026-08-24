import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    FLASK_DEBUG = (
        os.getenv("FLASK_DEBUG", "false").lower() == "true"
    )

    TOKENROUTER_BASE_URL = os.getenv(
        "TOKENROUTER_BASE_URL",
        "https://beta.token-router.org/v1",
    )

    TOKENROUTER_API_KEY = os.getenv(
        "TOKENROUTER_API_KEY",
        "",
    )

    TOKENROUTER_MODEL = os.getenv(
        "TOKENROUTER_MODEL",
        "",
    )


settings = Settings()