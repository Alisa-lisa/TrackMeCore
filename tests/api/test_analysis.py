from ..conftest import clean_up, user_setup


USER_PAYLOAD = {"name": "test1", "password": "123456", "email": "test@email.com"}


def test_simple_analysis(client):
    token = user_setup(client, USER_PAYLOAD)

    attribute = 13
    # setup one tracking entry
    entry = [
        {
            "topic_id": 1,
            "comment": "some comment",
            "estimation": 4,
            "attribute": attribute,
            "time": "2021-12-21 12:44:52",
        }
    ]
    client.post("/track/save", json=entry, headers={"token": token, "access-token": "test"})

    report = client.get(f"/analytic/analyze?attribute={attribute}", headers={"token": token, "access-token": "test"})

    # simple feature with estimation
    assert report.status_code == 200
    assert not report.json()["enough_data"]
    assert report.json()["recap"]["total"] > 0
    assert report.json()["recap"]["time_structure"][1]["count"] > 0
    assert report.json()["recap"]["time_structure"][1]["min"] > 0
    assert report.json()["recap"]["start"] == report.json()["recap"]["end"]


def test_missing_attribute(client):
    token = user_setup(client, USER_PAYLOAD, True)
    report_missing = client.get("/analytic/analyze?attribute=0", headers={"token": token, "access-token": "test"})

    assert report_missing.status_code == 200
    assert report_missing.json()["recap"]["total"] == 0


def test_binary_feature_analysis(client):
    token = user_setup(client, USER_PAYLOAD, True)
    binary_attribute = 6  # meditations as a default param
    entry = [{"topic_id": 2, "attribute": binary_attribute}]
    client.post("/track/save", json=entry, headers={"token": token, "access-token": "test"})

    report = client.get(
        f"/analytic/analyze?attribute={binary_attribute}", headers={"token": token, "access-token": "test"}
    )

    # simple feature with estimation
    assert report.status_code == 200
    assert "min" not in report.json()["recap"]["time_structure"][1].keys()

    # TODO: big trend test
    # special_attribute = 4
    # post_entry = []
    # for i in range(10, 26):
    #     post_entry.append({"topic_id": 1, "time": f"2021-01-{i} 00:00:00",
    # "estimation": 4, "attribute": special_attribute})
    # client.post("/track/save", json=post_entry, headers={"token": token, "access-token": "test"})
    #
    # # extended_report = client.get(f"/analytic/analyze?attribute={special_attribute}",
    # headers={"token": token, "access-token": "test"})
    # #
    # # assert extended_report.status_code == 200
    # # assert extended_report.json()["recap"]["total"] > 14
    # # assert "trend" in extended_report.json().keys()


def test_multifactor_analysis_pearson(client):
    token = user_setup(client, USER_PAYLOAD, True)

    # TODO: should go with a big test -> need a factory =)
    assert True

    # clean up
    clean_up(client, USER_PAYLOAD, token)
