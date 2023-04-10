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