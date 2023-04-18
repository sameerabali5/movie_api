from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_character():
    response = client.get("/characters/7421")
    assert response.status_code == 200

    with open("test/characters/7421.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_character_2():
    response = client.get("/characters/5011")
    assert response.status_code == 200

    with open("test/characters/5011.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_characters():
    response = client.get("/characters/")
    assert response.status_code == 200

    with open("test/characters/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_sort_filter():
    response = client.get("/movies/?name=big&limit=50&offset=0&sort=rating")
    assert response.status_code == 200

    with open(
        "test/movies/movies-name=big&limit=50&offset=0&sort=rating.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_sort_filter_2():
    response = client.get("/movies/?name=big&limit=50&offset=0&sort=year")
    assert response.status_code == 200

    with open(
        "test/movies/movies-name=big&limit=50&offset=0&sort=year.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_sort_filter_3():
    response = client.get("/movies/?name=big&limit=50&offset=0&sort=movie_title")
    assert response.status_code == 200

    with open(
        "test/movies/movies-name=big&limit=50&offset=0&sort=movie_title.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_404():
    response = client.get("/movies/1")
    assert response.status_code == 404