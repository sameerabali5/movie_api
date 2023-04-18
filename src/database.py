import csv
import os
import io
from supabase import Client, create_client

print("reading movies")


# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.
supabase_api_key = os.environ.get("SUPABASE_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")

supabase: Client = create_client(supabase_url, supabase_api_key)

sess = supabase.auth.get_session()

# TODO: Below is purely an example of reading and then writing a csv from supabase.
# You should delete this code for your working example.

# START PLACEHOLDER CODE

# Reading in the log file from the supabase bucket
log_csv = (
    supabase.storage.from_("movie-api")
    .download("movie_conversations_log.csv")
    .decode("utf-8")
)

logs = []
for row in csv.DictReader(io.StringIO(log_csv), skipinitialspace=True):
    logs.append(row)


# Writing to the log file and uploading to the supabase bucket
def upload_new_log():
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=["post_call_time", "movie_id_added_to"]
    )
    csv_writer.writeheader()
    csv_writer.writerows(logs)
    supabase.storage.from_("movie-api").upload(
        "movie_conversations_log.csv",
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )


# END PLACEHOLDER CODE

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
    lines0 = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    ]

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

number_of_lines = {}
with open('lines.csv', mode="r", encoding="utf8") as csv_file:
    for row in csv.DictReader(csv_file):
        t = (row["character_id"], row["movie_id"])
        if t not in number_of_lines.keys():
            number_of_lines[t] = 1
        else:
            number_of_lines[t] += 1


conversation_id_lines = {}
with open('lines.csv', mode="r", encoding="utf8") as csv_file:
    for row in csv.DictReader(csv_file):
        conv = row["conversation_id"]
        dialogue = row["line_text"]
        if conv not in conversation_id_lines.keys():
            conversation_id_lines.setdefault(conv, []).append(dialogue)
        else:
            conversation_id_lines[conv].append(dialogue)

#between characters and lines
sortedLines = dict(sorted(number_of_lines.items(), key=lambda i: -int(i[1])))

# sort characters
sortedCharacters = sorted(charactersO, key=lambda d: d['name'])
sortedMovies= sorted(charactersO, key=lambda d: movies[d['movie_id']]["title"])

# sort movies
sortedTitle = sorted(moviesO, key=lambda d: d['title'])
sortedYear = sorted(moviesO, key=lambda d: d['year'])
sortedRating = sorted(moviesO, key=lambda d: -float(d['imdb_rating']))

#sort lines
sortedLineSort = sorted(lines0, key=lambda d: d['line_sort'])
sortedLineText = sorted(lines0, key=lambda d: d['line_text'])
sortedLineId = sorted(lines0, key=lambda d: d['line_id'])