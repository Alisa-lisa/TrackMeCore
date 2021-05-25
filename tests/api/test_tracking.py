import uuid
from ..conftest import clean_up, user_setup


USER_PAYLOAD = {"name": "test1", "password": "123456", "email": "test@email.com"}
ENTRY = {
    "topic_id": 1,
    "comment": "some comment",
    "estimation": 4,
    "attributes": [
        {
            "id": 1,
            "name": "mood",
            "topic_id": 1,
        }
    ],
}


def test_add_tracking_entry(client):
    token = user_setup(client, USER_PAYLOAD)

    track = client.post("/track/save", json=ENTRY, headers={"token": token})

    assert track.status_code == 200
    assert track.json()


def test_malformed_tracking_entry(client):
    token = user_setup(client, USER_PAYLOAD, True)

    track = client.post("/track/save", json=ENTRY, headers={"token": str(uuid.uuid4())})
    assert track.status_code == 404

    entry = ENTRY.copy()
    entry["topic_id"] = 10
    track2 = client.post("/track/save", json=entry, headers={"token": token})
    assert not track2.json()


def test_update_tracking_entry(client):
    token = user_setup(client, USER_PAYLOAD, True)

    entries = client.get("/track/filter?topics=1&comments=false", headers={"token": token})
    assert len(entries.json()) >= 1
    print(f"these are entries {entries.json()}")
    entry = entries.json()[0]

    update = client.put("/track/update", headers={"token": token}, json={"id": entry["id"], "comment": "lol"})
    assert update.json()

    clean_up(client, USER_PAYLOAD, token)
