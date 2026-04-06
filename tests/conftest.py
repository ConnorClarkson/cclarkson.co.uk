import pytest

from app import create_app
from config import TestConfig


@pytest.fixture(scope="session")
def app():
    application = create_app(config_class=TestConfig)
    yield application


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()
