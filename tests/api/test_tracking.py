import uuid
from ..conftest import clean_up, user_setup
from trackme.tracking.types.tracking import MentalBalanceTagEnum as mne


USER_PAYLOAD = {"name": "test1", "password": "123456", "email": "test@email.com"}
ENTRIES = [{"topic_id": 1, "comment": "some comment", "estimation": 4, "attribute": 1}]


def test_add_fast_tracking_entry(client):
    token = user_setup(client, USER_PAYLOAD)

    entry = [{"topic_id": None, "comment": "some comment", "estimation": 4, "attribute": 1}]

    track = client.post("/track/save", json=entry, headers={"token": token, "access-token": "test"})

    assert track.status_code == 200
    assert track.json()


def test_add_story(client):
    token = user_setup(client, USER_PAYLOAD, True)
    entry = [
        {"topic_id": 1, "comment": "paaaain", "estimation": 2, "attribute": 2, "balance_tag": "fun"},
        {"topic_id": 1, "comment": "mooood", "estimation": 3, "attribute": 1, "time": "2021-01-01 00:00:00"},
        {"topic_id": 1, "attribute": 3},
    ]

    track = client.post("/track/save", json=entry, headers={"token": token, "access-token": "test"})

    assert track.status_code == 200
    assert track.json()


def test_malformed_tracking_entry(client):
    token = user_setup(client, USER_PAYLOAD, True)

    track = client.post(
        "/track/save",
        json=ENTRIES,
        headers={"token": str(uuid.uuid4()), "access-token": "test"},
    )
    assert track.status_code == 404

    entry = ENTRIES.copy()
    entry[0]["topic_id"] = 10
    track2 = client.post("/track/save", json=entry, headers={"token": token, "access-token": "test"})
    assert not track2.json()


def test_filter_and_update_tracking_entry(client):
    token = user_setup(client, USER_PAYLOAD, True)

    entries = client.get("/track/filter?comments=true", headers={"token": token, "access-token": "test"})

    assert len(entries.json()) == 3

    entries_body = entries.json()
    assert entries_body[0]["balance_tag"] is not None
    assert entries_body[0]["balance_tag"] == mne.fun

    entry = entries.json()[0]
    diff_time = [e for e in entries.json() if e["comment"] == "mooood"][0]
    assert entry["created_at"] != diff_time["created_at"]

    update = client.put(
        "/track/update",
        headers={"token": token, "access-token": "test"},
        json={"id": entry["id"], "comment": "lol"},
    )
    assert update.json()


def test_delete_entry(client):
    token = user_setup(client, USER_PAYLOAD, True)

    entries = client.get("/track/filter?comments=true", headers={"token": token, "access-token": "test"})
    assert len(entries.json()) == 3
    delete_id = entries.json()[0]["id"]

    deleted = client.delete(
        "/track/delete",
        json=[delete_id],
        headers={"token": token, "access-token": "test"},
    )

    assert deleted.status_code == 200
    assert deleted.json()
    entries = client.get("/track/filter?comments=true", headers={"token": token, "access-token": "test"})
    assert len(entries.json()) == 2

    clean_up(client, USER_PAYLOAD, token)
