from fastapi.testclient import TestClient
from src.api.server import app
import json
client = TestClient(app)

def test_get_line():
    response = client.get("/lines/5924")
    assert response.status_code == 200

    with open("test/lines/5924.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_conversations():
    response = client.get("/conversations/46803")
    assert response.status_code == 200

    with open("test/conversations/46803.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_lines():
    response = client.get("/lines/")
    assert response.status_code == 200

    with open("test/lines/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_sort_filter():
    response = client.get(
        "/lines/?name=10&limit=50&offset=0&sort=line_id"
    )
    assert response.status_code == 200

    with open(
        "test/lines/lines-name=10&limit=50&offset=0&sort=line_id.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_sort_filter_2():
    response = client.get(
        "/lines/?name=10&limit=50&offset=0&sort=line_sort"
    )
    assert response.status_code == 200

    with open(
        "test/lines/lines-name=10&limit=50&offset=0&sort=line_sort.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_sort_filter_3():
    response = client.get(
        "/lines/?name=10&limit=50&offset=0&sort=line_text"
    )
    assert response.status_code == 200

    with open(
        "test/lines/lines-name=10&limit=50&offset=0&sort=line_text.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_404_1():
    response = client.get("/lines/3")
    assert response.status_code == 404

def test_404_2():
    response = client.get("/conversations/83074")
    assert response.status_code == 404
