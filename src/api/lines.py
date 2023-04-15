from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
router = APIRouter()

@router.get("/lines/{line_id}", tags=["lines"])
def get_line(line_id: str):
    """
    This endpoint returns a single line by its identifier. For each line it returns:
    * 'character_id': the internal id of the character.
    * 'name': the name of the character.
    * `movie_id`: the internal id of the movie.
    * `title`: The title of the movie.
    * `line': the line said by character in the movie.
    """
    lines = db.lines
    characters = db.characters
    movies = db.movies
    if line_id in lines.keys():
        return (
            {
                "character_id": lines[line_id]["character_id"],
                "name": characters[lines[line_id]["character_id"]]["name"],
                "movie_id": lines[line_id]["movie_id"],
                "title": movies[lines[line_id]["movie_id"]]["title"],
                "line": lines[line_id]["line_text"]
            }
        )
    json = None
    if json is None:
        raise HTTPException(status_code=404, detail="line not found.")
    return json

@router.get("/conversations/{conversation_id}", tags=["lines"])
def get_conversations(conversation_id: str):
    """
    This endpoint returns a single conversation by its identifier.
    For each conversation_id it returns:
    * `movie_id`: the internal id of the movie in which the conversation takes place.
    * `title`: The title of the movie.
    * 'char1_name': name of character1 in conversation.
    * 'char2_name': name of character2 in conversation.
    * 'dialogue: a list of line_texts that occurred between both characters
    for that specific
                conversation_id
    """
    characters = db.characters
    conversations = db.conversations
    movies = db.movies
    conversation_id_lines = db.conversation_id_lines
    if conversation_id in conversations.keys():
        return (
            {
                "movie_id": conversations[conversation_id]["movie_id"],
                "title": movies[conversations[conversation_id]["movie_id"]]
                ["title"],
                "char1_name": characters[conversations[conversation_id]
                ["character1_id"]]["name"],
                "char2_name": characters[conversations[conversation_id]
                ["character2_id"]]["name"],
                "dialogue": conversation_id_lines.get(conversation_id)
            }
        )
    json = None
    if json is None:
        raise HTTPException(status_code=404, detail="conversation not found.")

    return json

class line_sort_options(str, Enum):
    line_id = "line_id"
    line_sort = "line_sort"
    line_text = "line_text"

@router.get("/lines/", tags=["lines"])
def list_lines(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: line_sort_options = line_sort_options.line_id,
):
    """
    This endpoint returns a list of lines. For each line it returns:
    * 'line_id': The internal id of the line
    * 'line_sort': The internal id of the line sort
    * `movie_title`: The title of the movie.
    * 'character_id': the internal id of the character in the movie
    * `num_of_lines': The total number of lines the character has in the movie

    You can filter for lines whose line_text contain a string by using the
    `word` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `line_sort` - Sort by line_sort in ascending order.
    * `line_text` - Sort by line_text alphabetically, breaking ties using character_id.
    * `line_id` - Sort by line_id, in ascending order.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    # accessing movies database
    sortedLineSort = db.sortedLineSort
    sortedLineText = db.sortedLineText
    sortedLineId = db.sortedLineId

    movies = db.movies

    lst = []

    if sort == line_sort_options.line_id:
        lst = sortedLineId
    if sort == line_sort_options.line_text:
        lst = sortedLineText
    if sort == line_sort_options.line_sort:
        lst = sortedLineSort

    if name != "":
        lst = list(filter(lambda x: name.lower() in x["line_text"].lower(), lst))

    json = []
    for dict in lst:
        x = {
                "line_id": int(dict["line_id"]),
                "character_id": int(dict["character_id"]),
                "movie_title": movies[dict["movie_id"]]["title"],
                "line_sort": dict["line_sort"],
                "line_text": dict["line_text"]
        }
        if len(json) < limit:
            json.append(x)
        else:
            break
    json = json[offset: len(json)]
    return json
