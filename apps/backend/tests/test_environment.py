import os

from dotenv import load_dotenv


def test_environment_configuration_loads():
    load_dotenv()

    assert os.environ.get("TOKENROUTER_API_KEY")
    assert os.environ.get("TOKENROUTER_BASE_URL")