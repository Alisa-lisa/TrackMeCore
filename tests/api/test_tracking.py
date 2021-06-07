import uuid
from ..conftest import clean_up, user_setup


USER_PAYLOAD = {"name": "test1", "password": "123456", "email": "test@email.com"}
ENTRIES = [{"topic_id": 1, "comment": "some comment", "estimation": 4, "attribute": 1}]


def test_add_fast_tracking_entry(client):
    token = user_setup(client, USER_PAYLOAD)

    entry = [{"topic_id": None, "comment": "some comment", "estimation": 4, "attribute": 1}]

    track = client.post("/track/save", json=entry, headers={"token": token})

    assert track.status_code == 200
    assert track.json()


def test_add_story(client):
    token = user_setup(client, USER_PAYLOAD, True)
    entry = [
        {"topic_id": 1, "comment": "paaaain go", "estimation": -2, "attribute": 2},
        {"topic_id": 1, "comment": "mooood", "estimation": 3, "attribute": 1},
    ]

    track = client.post("/track/save", json=entry, headers={"token": token})

    assert track.status_code == 200
    assert track.json()


def test_malformed_tracking_entry(client):
    token = user_setup(client, USER_PAYLOAD, True)

    track = client.post("/track/save", json=ENTRIES, headers={"token": str(uuid.uuid4())})
    assert track.status_code == 404

    entry = ENTRIES.copy()
    entry[0]["topic_id"] = 10
    track2 = client.post("/track/save", json=entry, headers={"token": token})
    assert not track2.json()


def test_filter_and_update_tracking_entry(client):
    token = user_setup(client, USER_PAYLOAD, True)

    entries = client.get("/track/filter?comments=true", headers={"token": token})
    assert len(entries.json()) == 3
    entry = entries.json()[0]

    update = client.put("/track/update", headers={"token": token}, json={"id": entry["id"], "comment": "lol"})
    assert update.json()


def test_delete_entry(client):
    token = user_setup(client, USER_PAYLOAD, True)

    entries = client.get("/track/filter?comments=true", headers={"token": token})
    assert len(entries.json()) == 3
    delete_id = entries.json()[0]["id"]

    deleted = client.delete("/track/delete", json=[delete_id], headers={"token": token})

    assert deleted.status_code == 200
    assert deleted.json()
    entries = client.get("/track/filter?comments=true", headers={"token": token})
    assert len(entries.json()) == 2

    clean_up(client, USER_PAYLOAD, token)
