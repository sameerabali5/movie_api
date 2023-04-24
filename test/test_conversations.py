from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

def test_get_post_1():
    response = client.get("/conversations/83074")
    assert response.status_code == 200

    #added a new conversation_id: 83074
    with open("test/conversations/post/83074.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_get_post_2():
    response = client.get("/characters/5011")
    assert response.status_code == 200

    # added a new conversation_id: 83074, hence, the number of lines increased by 1
    with open("test/conversations/post/5011.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)