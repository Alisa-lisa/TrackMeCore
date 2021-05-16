import pytest


def test_add_user(client):
    response = client.post("/user/register", json={"name": "lolol", "password": "123456", "email": "lol@email.com"})

    assert response.status_code == 200
    assert response.json()


def test_add_existing_email_new_user(client):
    response = client.post("/user/register", json={"name": "lolol1", "password": "123456", "email": "lol@email.com"})

    assert response.status_code == 400


def test_auth_user(client):
    response = client.post("/user/auth", json={"name": "lolol", "password": "123456", "email": "lol@email.com"})

    assert response.status_code == 200

    failed_auth1 = client.post(
        "/user/auth", json={"name": "lolol_wrong", "password": "123456", "email": "lol@email.com"}
    )
    assert failed_auth1.status_code == 403


@pytest.mark.skip("wait until update user data is implemented")
def test_successful_update_user(client):
    proper_token = client.post("/user/auth", json={"name": "lolol", "password": "123456"}).json()
    update_response = client.put("/user/update", json={"name": "hehehe"}, headers={"token": proper_token})

    assert update_response.status_code == 200
    assert update_response.json()


@pytest.mark.skip("wait until update user data is implemented")
def test_wrong_user_update(client):
    update_response = client.put("/user/update", json={"name": "hehehe"}, headers={"token": "sfsdfsfds"})

    assert update_response.status_code == 400


def test_failed_remove_user(client):
    wrong_delete = client.delete(
        "/user/delete", json={"name": "hehehe", "password": "123456"}, headers={"token": "real token"}
    )

    assert not wrong_delete.json()


def test_successful_remove_user(client):
    proper_token = client.post("/user/auth", json={"name": "lolol", "password": "123456"}).json()
    wrong_delete = client.delete(
        "/user/delete", json={"name": "lolol", "password": "123456"}, headers={"token": proper_token}
    )

    assert wrong_delete.status_code == 200
    assert wrong_delete.json()
