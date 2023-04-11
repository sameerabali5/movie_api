import csv
import collections

print("reading movies")

with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    moviesO = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    ]

with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    movies = csv.DictReader(csv_file)
    movies = {row.pop("movie_id"): row for row in movies}

with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    charactersO = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    ]

with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    characters = csv.DictReader(csv_file)
    characters = {row.pop("character_id"): row for row in characters}

with open("conversations.csv", mode="r", encoding="utf8") as csv_file:
    conversations = csv.DictReader(csv_file)
    conversations = {row.pop("conversation_id"): row for row in conversations}

with open("lines.csv", mode="r", encoding="utf8") as csv_file:
    lines = csv.DictReader(csv_file)
    lines = {row.pop("line_id"): row for row in lines}

number_of_lines = {}
with open('lines.csv', mode="r", encoding="utf8") as csv_file:
    for row in csv.DictReader(csv_file):
        t = (row["character_id"], row["movie_id"])
        if t not in number_of_lines.keys():
            number_of_lines[t] = 1
        else:
            number_of_lines[t] += 1

# sort characters
sortedCharacters = sorted(charactersO, key=lambda d: d['name'])
sortedMovies= sorted(charactersO, key=lambda d: movies[d['movie_id']]["title"])
sortedLines = dict(sorted(number_of_lines.items(), key=lambda i: -int(i[1])))

# print(sortedMovies)
# sortedMovies = sorted(charactersO, key=lambda d: d['movie_id'])


# sort movies
# sortedTitle = sorted(moviesO, key=lambda d: d['title'])
# sortedYear = sorted(charactersO, key=lambda d: d['year'])
# sortedRating = sorted(charactersO, key=lambda d: d['imdb_rating'])




