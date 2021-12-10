from ..conftest import clean_up, user_setup


USER_PAYLOAD = {"name": "test1", "password": "123456", "email": "test@email.com"}
ENTRIES = [{"topic_id": 1, "comment": "some comment", "estimation": 4, "attribute": 1}]


def test_add_fast_tracking_entry(client):
    token = user_setup(client, USER_PAYLOAD)

    attribute = 23
    # setup one tracking entry
    entry = [{"topic_id": None, "comment": "some comment", "estimation": 4, "attribute": attribute}]
    client.post("/track/save", json=entry, headers={"token": token, "access-token": "test"})

    report = client.get(f"/analytic/analyze?attribute={attribute}", headers={"token": token, "access-token": "test"})

    assert report.status_code == 200
    assert not report.json()["enough_data"]
    assert report.json()["recap"]["start"] == report.json()["recap"]["end"]

    report_missing = client.get("/analytic/analyze?attribute=0", headers={"token": token, "access-token": "test"})

    assert report_missing.status_code == 200
    assert report_missing.json()["recap"]["total"] == 0

    # clean up
    clean_up(client, USER_PAYLOAD, token)
