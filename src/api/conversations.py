from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
import sqlalchemy


# FastAPI is inferring what the request body should look like
# based on the following two classes.
class LinesJson(BaseModel):
    character_id: int
    line_text: str


class ConversationJson(BaseModel):
    character_1_id: int
    character_2_id: int
    lines: List[LinesJson]

router = APIRouter()


@router.post("/movies/{movie_id}/conversations/", tags=["movies"])
def add_conversation(movie_id: int, conversation: ConversationJson):
    """
    This endpoint adds a conversation to a movie. The conversation is represented
    by the two characters involved in the conversation and a series of lines
    between those characters in the movie.

    The endpoint ensures that all characters are part of the referenced movie,
    that the characters are not the same, and that the lines of a conversation
    match the characters involved in the conversation.

    Line sort is set based on the order in which the lines are provided in the
    request body.

    The endpoint returns the id of the resulting conversation that was created.
    """
    char1 = conversation.character_1_id
    char2 = conversation.character_2_id
    conn = db.engine.connect()

    #Error 1
    moviecheck = conn.execute(
        sqlalchemy.text(f"""SELECT COUNT(*) FROM movies "
                            "WHERE movie_id = {movie_id}""")).fetchone()
    if moviecheck[0] == 0:
        raise HTTPException(status_code=404,
                            detail="Movie not found.")

    #Error 2
    movie1 = conn.execute(
        sqlalchemy.text(f"""SELECT COUNT(*) FROM characters "
                        "WHERE character_id = {char1}""")).fetchone()
    movie2 = conn.execute(
        sqlalchemy.text(f"""SELECT COUNT(*) FROM characters "
                        "WHERE character_id = {char2}""")).fetchone()
    valid_1 = movie1[0]
    valid_2 = movie2[0]
    if valid_1 == 0 or valid_2 == 0:
        raise HTTPException(status_code=404,
                            detail="Character not found.")

    #Error 3
    movie_char1 = conn.execute(
        sqlalchemy.text(f"""SELECT movie_id FROM characters "
                        "WHERE character_id = {char1}""")).fetchone()
    movie_char2 = conn.execute(
        sqlalchemy.text(f"""SELECT movie_id FROM characters "
                        "WHERE character_id = {char2}""")).fetchone()
    if (movie_char1[0]) != movie_id or (movie_char2[0]) != movie_id:
        raise HTTPException(status_code=404,
                            detail="Characters not in movie.")
    #Error 4
    if char1 == char2:
        raise HTTPException(status_code=404,
                            detail="Characters are not unique.")


    lastConvo = conn.execute(
        sqlalchemy.text(
            """SELECT conversation_id FROM conversations 
            ORDER BY conversation_id DESC LIMIT 1;"""))
    newConvoId = lastConvo.fetchone()[0] + 1
    with db.engine.begin() as conn:
        conn.execute(
            sqlalchemy.insert(db.conversations),
            [
                {
                    "conversation_id": newConvoId,
                    "character1_id": conversation.character_1_id,
                    "character2_id": conversation.character_2_id,
                    "movie_id": movie_id
                }
            ],
        )

    with db.engine.begin() as conn:
        for line in range(len(conversation.lines)):
            access_id = conversation.lines[0].character_id
            line_text = conversation.lines[0].line_text
            if access_id == char1 or access_id == char2:
                line_sort = line + 1
                lastLine = conn.execute(
                    sqlalchemy.text(
                        """SELECT line_id FROM lines 
                        ORDER BY line_id DESC LIMIT 1;"""))
                newLineId = lastLine.fetchone()[0] + 1
                conn.execute(
                    sqlalchemy.insert(db.lines),
                    [
                        {
                            "line_id": newLineId,
                            "character_id": access_id,
                            "movie_id": movie_id,
                            "conversation_id": newConvoId,
                            "line_sort": line_sort,
                            "line_text": line_text
                        }
                    ])
                return newConvoId
        raise HTTPException(status_code=404, detail="Invalid line.")



