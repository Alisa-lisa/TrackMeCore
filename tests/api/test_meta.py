def test_topics(client):
    response = client.get("/meta/topics")

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_attributes(client):
    response = client.get("/meta/attributes?topic_id=1")

    assert response.status_code == 200
    assert len(response.json()) >= 9
