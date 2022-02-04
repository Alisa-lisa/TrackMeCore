import uuid
from ..conftest import clean_up, user_setup
from trackme.tracking.types.tracking import MentalBalanceTagEnum as mne
import os
import csv


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
    balance_entry = [entry for entry in entries_body if entry["comment"] == "paaaain"][0]
    assert balance_entry["balance_tag"] is not None
    assert balance_entry["balance_tag"] == mne.fun

    mood_entry = [entry for entry in entries_body if entry["comment"] == "mooood"][0]
    assert mood_entry["created_at"] != balance_entry["created_at"]

    update = client.put(
        "/track/update",
        headers={"token": token, "access-token": "test"},
        json={"id": mood_entry["id"], "comment": "lol"},
    )
    assert update.json()


def test_not_allowed_dowload(client):
    download_response = client.get("/track/download", headers={"token": str(uuid.uuid4()), "access-token": "test"})

    assert download_response.status_code == 404


def test_proper_download(client):
    token = user_setup(client, USER_PAYLOAD, True)
    download_response = client.get("/track/download", headers={"token": token, "access-token": "test"})

    assert download_response.status_code == 200
    for filename in os.listdir(f"{os.getcwd()}/files"):
        with open(f"{os.getcwd()}/files/{filename}", 'r') as download:
            reader = csv.reader(download)
            assert len(list(reader)) > 1
        os.remove(f"./files/{filename}")


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
