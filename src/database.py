import csv
import os
import io
from supabase import Client, create_client
from sqlalchemy import create_engine
import sqlalchemy
import dotenv

# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.
dotenv.load_dotenv()
supabase_api_key = os.environ.get("SUPABASE_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")

if supabase_api_key is None or supabase_url is None:
    raise Exception(
        "You must set the SUPABASE_API_KEY and SUPABASE_URL environment variables."
    )

supabase: Client = create_client(supabase_url, supabase_api_key)

sess = supabase.auth.get_session()

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    # return "postgresql://postgres:2YUGg4QRNN370eTU@db.uikcgyqdygsookfnwapg.supabase.co:5432/postgres"
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url())

metadata_obj = sqlalchemy.MetaData()
movies = sqlalchemy.Table("movies", metadata_obj, autoload_with=engine)

metadata_obj = sqlalchemy.MetaData()
characters = sqlalchemy.Table("characters", metadata_obj, autoload_with=engine)

metadata_obj = sqlalchemy.MetaData()
lines = sqlalchemy.Table("lines", metadata_obj, autoload_with=engine)

metadata_obj = sqlalchemy.MetaData()
conversations = sqlalchemy.Table("conversations", metadata_obj, autoload_with=engine)





# num_of_lines = conn.execute(sqlalchemy.text(num_of_lines))
# # characters = conn.execute(sqlalchemy.text(characters))
# # conversations = conn.execute(sqlalchemy.text(conversations))
# # lines = conn.execute(sqlalchemy.text(lines))
# for row in num_of_lines:
#     print(row)

# # Reading in the log file from the supabase bucket
# lines_csv = (
#     supabase.storage.from_("movie-api")
#     .download("lines.csv")
#     .decode("utf-8")
# )
#
# conversations_csv = (
#     supabase.storage.from_("movie-api")
#     .download("conversations.csv")
#     .decode("utf-8")
# )
#
# lines_to_add = []
# conversations_to_add = []
#
# lines_logs = list(csv.DictReader(io.StringIO(lines_csv),
#                                  skipinitialspace=True))
#
# lines0 = [{k: v for k, v in row.items()} for row in
#           csv.DictReader(io.StringIO(lines_csv), skipinitialspace=True)]
#
# lines = {row.pop("line_id"): row for row in
#          csv.DictReader(io.StringIO(lines_csv), skipinitialspace=True)}
#
# number_of_lines = {}
# for row in lines_logs:
#     t = (row["character_id"], row["movie_id"])
#     number_of_lines[t] = number_of_lines.get(t, 0) + 1
#
# conversation_id_lines = {}
# for row in lines_logs:
#     conversation_id_lines.setdefault(row["conversation_id"], []).\
#         append(row["line_text"])
#
#
# conversations_logs = []
# for row in csv.DictReader(io.StringIO(conversations_csv),
#                           skipinitialspace=True):
#     conversations_logs.append(row)
#
# conversations = {row.pop("conversation_id"): row for row in
#                  csv.DictReader(io.StringIO(conversations_csv),
#                                 skipinitialspace=True)}
#
#
# # Writing to the log file and uploading to the supabase bucket
# def update_lines_log():
#     output = io.StringIO()
#     csv_writer = csv.DictWriter(
#         output, fieldnames=["line_id", "character_id", "movie_id",
#                             "conversation_id", "line_sort", "line_text"]
#     )
#     csv_writer.writeheader()
#     csv_writer.writerows(lines_logs)
#
#     for row in lines_to_add:
#         lines0.append({k: v for k, v in row.items()})
#
#         lines[row["line_id"]] = row
#
#         t = (row["character_id"], row["movie_id"])
#         number_of_lines[t] += 1
#
#         conv = row["conversation_id"]
#         dialogue = row["line_text"]
#         conversation_id_lines.setdefault(conv, []).append(dialogue)
#     lines_to_add.clear()
#
#     supabase.storage.from_("movie-api").upload(
#         "lines.csv",
#         bytes(output.getvalue(), "utf-8"),
#         {"x-upsert": "true"},
#     )
# def update_convos_log():
#     output = io.StringIO()
#     csv_writer = csv.DictWriter(
#         output, fieldnames=["conversation_id", "character1_id", "character2_id",
#                             "movie_id"]
#     )
#     csv_writer.writeheader()
#     csv_writer.writerows(conversations_logs)
#
#     for row in conversations_to_add:
#         conversations[row["conversation_id"]] = row
#     conversations_to_add.clear()
#
#     supabase.storage.from_("movie-api").upload(
#         "conversations.csv",
#         bytes(output.getvalue(), "utf-8"),
#         {"x-upsert": "true"},
#     )
#
# with open("movies.csv", mode="r", encoding="utf8") as csv_file:
#     moviesO = [
#         {k: v for k, v in row.items()}
#         for row in csv.DictReader(csv_file, skipinitialspace=True)
#     ]
#
# with open("movies.csv", mode="r", encoding="utf8") as csv_file:
#     movies = csv.DictReader(csv_file)
#     movies = {row.pop("movie_id"): row for row in movies}
#
#
# with open("characters.csv", mode="r", encoding="utf8") as csv_file:
#     charactersO = [
#         {k: v for k, v in row.items()}
#         for row in csv.DictReader(csv_file, skipinitialspace=True)
#     ]
#
# with open("characters.csv", mode="r", encoding="utf8") as csv_file:
#     characters = csv.DictReader(csv_file)
#     characters = {row.pop("character_id"): row for row in characters}
#
#
# #between characters and lines
# sortedLines = dict(sorted(number_of_lines.items(), key=lambda i: -int(i[1])))
#
# # sort characters
# sortedCharacters = sorted(charactersO, key=lambda d: d['name'])
# sortedMovies= sorted(charactersO, key=lambda d: movies[d['movie_id']]["title"])
#
# # sort movies
# sortedTitle = sorted(moviesO, key=lambda d: d['title'])
# sortedYear = sorted(moviesO, key=lambda d: d['year'])
# sortedRating = sorted(moviesO, key=lambda d: -float(d['imdb_rating']))
#
# #sort lines
# sortedLineSort = sorted(lines0, key=lambda d: d['line_sort'])
# sortedLineText = sorted(lines0, key=lambda d: d['line_text'])
# sortedLineId = sorted(lines0, key=lambda d: d['line_id'])