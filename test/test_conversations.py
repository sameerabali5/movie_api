from fastapi.testclient import TestClient
from src.api.server import app
from src import database as db

client = TestClient(app)


def test_post_1():
    response = client.post("/movies/615/conversations/", json={
                          "character_1_id": 9024,
                          "character_2_id": 9017,
                          "lines": [
                            {
                              "character_id": 9024,
                              "line_text": "testing post request through IDE"
                            }
                          ]
                        })
    assert response.status_code == 200
    lastConvo = db.conversations_logs[-1]
    conversation_id = int(lastConvo["conversation_id"])
    assert response.json() == conversation_id

def test_post_2():
    response = client.post("/movies/615/conversations/", json={
                          "character_1_id": 9024,
                          "character_2_id": 9024,
                          "lines": [
                            {
                              "character_id": 9024,
                              "line_text": "testing post request 1"
                            }
                          ]
                        })
    assert response.status_code == 404
    assert response.json() == {"detail": "Characters are not unique."}

def test_post_3():
    response = client.post("/movies/615/conversations/", json={
                          "character_1_id": 0,
                          "character_2_id": 1,
                          "lines": [
                            {
                              "character_id": 0,
                              "line_text": "testing post request 1"
                            }
                          ]
                        })
    assert response.status_code == 404
    assert response.json() == {"detail": "Characters not in movie."}

def test_post_4():
    response = client.post("/movies/617/conversations/", json={
                          "character_1_id": 0,
                          "character_2_id": 1,
                          "lines": [
                            {
                              "character_id": 0,
                              "line_text": "testing post request 1"
                            }
                          ]
                        })
    assert response.status_code == 404
    assert response.json() == {"detail": "Movie not found."}


def test_post_5():
    response = client.post("/movies/615/conversations/", json={
                          "character_1_id": 9024,
                          "character_2_id": 9017,
                          "lines": [
                            {
                              "character_id": 0,
                              "line_text": "testing post request 1"
                            }
                          ]
                        })
    assert response.status_code == 404
    assert response.json() == {"detail": "Invalid line."}

def test_post_6():
    response = client.post("/movies/615/conversations/", json={
                          "character_1_id": 9025,
                          "character_2_id": 9017,
                          "lines": [
                            {
                              "character_id": 0,
                              "line_text": "testing post request 1"
                            }
                          ]
                        })
    assert response.status_code == 404
    assert response.json() == {"detail": "Character not found."}