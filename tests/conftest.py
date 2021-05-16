from fastapi.testclient import TestClient
from trackme import app_factory
import pytest


# TODO: os dependent .env files?
@pytest.fixture(scope="session")
def client():
    app = app_factory()
    return TestClient(app)
