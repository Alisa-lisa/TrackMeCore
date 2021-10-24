from fastapi.testclient import TestClient
from trackme import app_factory
import pytest


# TODO: os dependent .env files?
@pytest.fixture(scope="session")
def client():
    app = app_factory()
    return TestClient(app)


def clean_up(client, user_payload, token):
    client.delete(
        "/user/delete",
        json=user_payload,
        headers={"token": token, "access-token": "test"},
    )


def user_setup(client, user_payload, skip=False):
    if not skip:
        client.post("/user/register", json=user_payload, headers={"access-token": "test"})
    return client.post("/user/auth", json=user_payload, headers={"access-token": "test"}).json()
