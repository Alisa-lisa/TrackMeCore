from datetime import datetime
from ..conftest import clean_up, user_setup

USER_PAYLOAD = {"name": "test1", "password": "123456", "email": "test@email.com"}
PROPER_ATTRIBUTE = {"topic_id": 2, "name": "sport", "icon_name": "lol"}


def test_topics(client):
    response = client.get("/meta/topics")

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_attributes(client):
    response = client.get("/meta/attributes?topic_id=1")

    assert response.status_code == 200
    assert len(response.json()) >= 3


def test_proper_create_attributes(client):
    # add a new attribute to physical topic (id=2)
    token = user_setup(client, USER_PAYLOAD)

    track = client.post(
        "/meta/attributes",
        json=PROPER_ATTRIBUTE,
        headers={"token": token, "access-token": "test"},
    )

    default_attributes = client.get(f"/meta/attributes?topic_id={PROPER_ATTRIBUTE['topic_id']}")
    custom_attributes = client.get(
        f"/meta/attributes?topic_id={PROPER_ATTRIBUTE['topic_id']}",
        headers={"token": token, "access-token": "test"},
    )

    assert track.status_code == 200
    assert track.json()["name"] == "sport"
    assert track.json()["active"]

    assert len(default_attributes.json()) < len(custom_attributes.json())


def test_hide_attribute(client):
    # hide and then reactivate an attribute
    token = user_setup(client, USER_PAYLOAD, True)
    url = f'/meta/attributes?topic_id={PROPER_ATTRIBUTE["topic_id"]}'
    attribute_to_update = client.get(url, headers={"token": token, "access-token": "test"}).json()[0]
    assert attribute_to_update["active"]

    data = {"id": attribute_to_update["id"], "active": False}
    updated = client.put("/meta/attributes", headers={"token": token, "access-token": "test"}, json=data)
    assert updated.status_code == 200
    assert updated.json()

    url = f'/meta/attributes?topic_id={PROPER_ATTRIBUTE["topic_id"]}'
    non_active_attribute = [
        a
        for a in client.get(url, headers={"token": token, "access-token": "test"}).json()
        if a["id"] == attribute_to_update["id"]
    ][0]
    assert non_active_attribute["id"] == attribute_to_update["id"]
    assert not non_active_attribute["active"]

    data = {"id": attribute_to_update["id"], "active": True}
    updated = client.put("/meta/attributes", headers={"token": token, "access-token": "test"}, json=data)


def test_proper_delete_attribute(client):
    token = user_setup(client, USER_PAYLOAD, True)
    url = f'/meta/attributes?topic_id={PROPER_ATTRIBUTE["topic_id"]}'
    attributes = client.get(url, headers={"token": token, "access-token": "test"})

    attribute_id = [a["id"] for a in attributes.json() if a["name"] == PROPER_ATTRIBUTE["name"]][0]

    deleted_attribue = client.delete(
        f"/meta/attributes?attribute_id={attribute_id}",
        headers={"token": token, "access-token": "test"},
    )

    assert deleted_attribue


def test_proper_create_experiment(client):
    token = user_setup(client, USER_PAYLOAD, True)
    experiment = client.post(
        "/meta/experiments", headers={"token": token, "access-token": "test"}, json={"name": "first experiment"}
    )

    assert experiment.status_code == 200
    assert experiment.json()["name"] == "first experiment"
    assert experiment.json()["closed_at"] is None


def test_no_experiment_can_be_cerated_wehn_previous_is_open(client):
    token = user_setup(client, USER_PAYLOAD, True)
    experiment = client.post(
        "/meta/experiments", headers={"token": token, "access-token": "test"}, json={"name": "first experiment"}
    )

    # assert experiment.status_code == ?  # TBD: better error and status codes handling
    assert experiment.json() is None


def test_close_old_experiment_and_create_new(client):
    token = user_setup(client, USER_PAYLOAD, True)
    all_experiments = client.get("/meta/experiments", headers={"token": token, "access-token": "test"})
    old_open_experiment = [exp for exp in all_experiments.json() if exp["closed_at"] is None][0]

    assert old_open_experiment["name"] == "first experiment"
    json = {"id": old_open_experiment["id"], "closed_at": datetime.today().isoformat()}
    close = client.put("/meta/experiments", headers={"token": token, "access-token": "test"}, json=json)

    assert close.status_code == 200
    assert close.json()

    experiment = client.post(
        "/meta/experiments", headers={"token": token, "access-token": "test"}, json={"name": "second experiment"}
    )
    assert experiment.status_code == 200
    assert experiment.json()["name"] == "second experiment"
    assert experiment.json()["closed_at"] is None

    all_experiments = client.get("/meta/experiments", headers={"token": token, "access-token": "test"})

    assert len(all_experiments.json()) > 1

    clean_up(client, USER_PAYLOAD, token)
