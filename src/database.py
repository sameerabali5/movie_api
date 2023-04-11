import csv

print("reading movies")

with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    movies = csv.DictReader(csv_file)
    movies = {row.pop("movie_id"): row for row in movies}

with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    characters = csv.DictReader(csv_file)
    characters = {row.pop("character_id"): row for row in characters}

with open("conversations.csv", mode="r", encoding="utf8") as csv_file:
    conversations = csv.DictReader(csv_file)
    conversations = {row.pop("conversation_id"): row for row in conversations}

with open("lines.csv", mode="r", encoding="utf8") as csv_file:
    lines = csv.DictReader(csv_file)
    lines = {row.pop("line_id"): row for row in lines}


# list_characters is a list of characters with required information
list_characters = []
for character_id in list(characters.keys()):
    list_characters.append({
        "character_id": int(character_id),
        "character": characters[character_id]["name"],
        "movie": movies[characters[character_id]["movie_id"]]["title"],
        "number_of_lines": sum(v["character_id"] ==
                               character_id for v in lines.values())
    })

# list_movies is a list of movies with required information
list_movies = []
for movie_id in list(movies.keys()):
    list_movies.append({
            "movie_id": int(movie_id),
            "movie_title": movies[movie_id]["title"],
            "year": movies[movie_id]["year"],
            "imdb_rating": float(movies[movie_id]["imdb_rating"]),
            "imdb_votes": int(movies[movie_id]["imdb_votes"])
        })



