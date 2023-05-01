from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
router = APIRouter()
import sqlalchemy
from sqlalchemy import inspect

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
    stmt = f"""SELECT
                    lines.character_id AS character_id,
                    characters.name AS name,
                    lines.movie_id AS movie_id,
                    movies.title AS title,
                    lines.line_text AS line
                FROM
                    lines
                    JOIN characters ON lines.character_id = characters.character_id
                    JOIN movies ON lines.movie_id = movies.movie_id
                WHERE
                    lines.line_id = {line_id}"""
    with db.engine.connect() as conn:
        result = conn.execute(sqlalchemy.text(stmt))
        for row in result:
            return (
                {
                    "character_id": row.character_id,
                    "name": row.name,
                    "movie_id": row.movie_id,
                    "title": row.title,
                    "line": row.line
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
    stmt = f"""SELECT
                conversations.movie_id AS movie_id,
                movies.title AS title,
                conversations.character1_id AS char1_id,
                conversations.character2_id as char2_id,
                char1.name AS name1,
                char2.name AS name2,
                array_agg(lines.line_text) AS dialogues
            FROM
                conversations
                JOIN movies ON conversations.movie_id = movies.movie_id
                JOIN characters AS char1 ON 
                    conversations.character1_id = char1.character_id
                JOIN characters AS char2 ON 
                    conversations.character2_id = char2.character_id
                JOIN lines on conversations.conversation_id = lines.conversation_id
            WHERE
                conversations.conversation_id = {conversation_id}
            GROUP BY
                conversations.movie_id,
                movies.title,
                conversations.character1_id,
                conversations.character2_id,
                char1.name,
                char2.name;"""

    with db.engine.connect() as conn:
        result = conn.execute(sqlalchemy.text(stmt))
        for row in result:
            return (
                {
                    "movie_id": row.movie_id,
                    "title": row.title,
                    "char1_name": row.name1,
                    "char2_name": row.name2,
                    "dialogue": row.dialogues
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
    * `line_text': The text for that specific line_id

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
    if sort == line_sort_options.line_id:
        order_by = db.lines.c.line_id
    elif sort == line_sort_options.line_text:
        order_by = db.lines.c.line_text
    elif sort == line_sort_options.line_sort:
        order_by = db.lines.c.line_sort
    else:
        assert False

    stmt = (
        sqlalchemy.select(
            db.lines.c.line_id,
            db.lines.c.character_id,
            db.lines.c.movie_id,
            db.lines.c.conversation_id,
            db.lines.c.line_sort,
            db.lines.c.line_text,
            db.movies.c.title
        )
        .select_from(
            db.lines.join(
                db.movies,
                db.lines.c.movie_id == db.movies.c.movie_id
            )
        )
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.lines.c.line_id)
    )

    if name != "":
        stmt = stmt.where(db.lines.c.line_text.ilike(f"%{name}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append({
                "line_id": row.line_id,
                "character_id": row.character_id,
                "movie_title": row.title,
                "line_sort": row.line_sort,
                "line_text": row.line_text
        })
    return json
