from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
import sqlalchemy
from sqlalchemy import func
router = APIRouter()

@router.get("/characters/{id}", tags=["characters"])
def get_character(id: str):
    """
    This endpoint returns a single character by its identifier. For each character
    it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `gender`: The gender of the character.
    * `top_conversations`: A list of characters that the character has the most
      conversations with. The characters are listed in order of the number of
      lines together. These conversations are described below.

    Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `gender`: The gender of the character.
    * `number_of_lines_together`: The number of lines the character has with the
      originally queried character.
    """

    def top_convos(charID, movieID):
        """Function returns the list of characters that the
        character has the most conversations with,
        sorted by number of lines together """
        stmt = f"""WITH convosQuery AS (
                        SELECT conversations.conversation_id
                        FROM conversations
                        WHERE movie_id = {movieID}
                            AND (character1_id = {charID} OR character2_id = {charID})
                    )
                    SELECT
                        characters.character_id,
                        characters.name,
                        characters.gender,
                        COUNT(lines.line_id) AS num_lines
                    FROM
                        conversations
                    JOIN
                        characters ON 
                        conversations.character1_id = 
                        characters.character_id
                            OR 
                            conversations.character2_id = 
                            characters.character_id
                    JOIN
                        convosQuery ON c
                        onversations.conversation_id = convosQuery.conversation_id
                    JOIN
                        lines ON conversations.conversation_id = lines.conversation_id
                    WHERE
                        characters.character_id != {charID}
                    GROUP BY
                        characters.character_id,
                        characters.name,
                        characters.gender
                    ORDER BY
                        num_lines DESC"""
        json = []
        with db.engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(stmt))
            for row in result:
                json.append(
                    {
                        "character_id": row.character_id,
                        "character": row.name,
                        "gender": row.gender,
                        "number_of_lines_together": row.num_lines
                    }
                )
        return json

    stmt = f"""SELECT characters.character_id, characters.name, movies.title,
                characters.gender, characters.movie_id
                FROM characters
                JOIN movies ON characters.movie_id = movies.movie_id
                WHERE characters.character_id = {id}
                GROUP BY characters.character_id, characters.name, movies.title
                ORDER BY characters.character_id;"""

    with db.engine.connect() as conn:
        result = conn.execute(sqlalchemy.text(stmt))
        for row in result:
            return {
                "character_id": row.character_id,
                "character": row.name,
                "movie": row.title,
                "gender": row.gender,
                "top_conversations": top_convos(row.character_id, row.movie_id)
            }

    json = None
    if json is None:
        raise HTTPException(status_code=404, detail="character not found.")
    return json

class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"

@router.get("/characters/", tags=["characters"])
def list_characters(
        name: str = "",
        limit: int = 50,
        offset: int = 0,
        sort: character_sort_options = character_sort_options.character,
):
    """
    This endpoint returns a list of characters. For each character it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `number_of_lines`: The number of lines the character has in the movie.

    You can filter for characters whose name contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `number_of_lines` - Sort by number of lines, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    if sort == character_sort_options.character:
        order_by = db.characters.c.name
    if sort == character_sort_options.movie:
        order_by = db.movies.c.title
    if sort == character_sort_options.number_of_lines:
        order_by = func.count(db.lines.c.line_id).desc()

    stmt = (sqlalchemy.select(
        db.characters.c.character_id,
        db.characters.c.name,
        db.movies.c.title,
        func.count(db.lines.c.line_id).label('num_lines')
        )
        .select_from(
            db.characters
            .join(db.movies,
                  db.characters.c.movie_id == db.movies.c.movie_id)
            .join(db.lines,
                  db.characters.c.character_id == db.lines.c.character_id))
        .group_by(db.characters.c.character_id, db.movies.c.title)
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.characters.c.character_id))
    if name != "":
        stmt = stmt.where(db.characters.c.name.ilike(f"%{name}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append({
                "character_id": row.character_id,
                "character": row.name,
                "movie": row.title,
                "number_of_lines": row.num_lines
            })
    return json

