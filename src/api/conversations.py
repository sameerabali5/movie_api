from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List


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

def append_line_logs(line_id, char_id, movie_id, conv_id, sort, text):
    """Appends information to respective arrays"""
    line = {
        "line_id": str(line_id),
        "character_id": str(char_id),
        "movie_id": str(movie_id),
        "conversation_id": str(conv_id),
        "line_sort": str(sort),
        "line_text": str(text)
    }
    db.lines_logs.append(line)
    db.lines_to_add.append(line)
    db.update_lines_log()

def append_conv_logs(conv_id, char1, char2, movie_id):
    """Appends information to respective arrays"""
    convo = {
        "conversation_id": str(conv_id),
        "character1_id": str(char1),
        "character2_id": str(char2),
        "movie_id": str(movie_id)
    }
    db.conversations_logs.append(convo)
    db.conversations_to_add.append(convo)
    db.update_convos_log()


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
    movies = db.movies
    characters = db.characters
    char1 = conversation.character_1_id
    char2 = conversation.character_2_id

    if str(movie_id) not in movies:
        raise HTTPException(status_code=404,
                            detail="Movie not found.")

    if str(char1) not in characters or str(char2) not in characters:
        raise HTTPException(status_code=404,
                            detail="Character not found.")

    movie_char1 = characters[str(char1)]["movie_id"]
    movie_char2 = characters[str(char2)]["movie_id"]

    if str(movie_id) != movie_char1 or str(movie_id) != movie_char2:
        raise HTTPException(status_code=404,
                            detail="Characters not in movie.")

    if char1 == char2:
        raise HTTPException(status_code=404,
                            detail="Characters are not unique.")

    for line in range(len(conversation.lines)):
        access_id = conversation.lines[0].character_id
        line_text = conversation.lines[0].line_text
        if access_id == char1 or access_id == char2:
            line_sort = line + 1
            lastConvo = db.conversations_logs[-1]
            conversation_id = int(lastConvo["conversation_id"]) + 1
            lastLine = db.lines_logs[-1]
            line_id = int(lastLine["line_id"]) + 1
            append_line_logs(line_id, access_id, movie_id,
                             conversation_id, line_sort, line_text)
            append_conv_logs(conversation_id, char1, char2, movie_id)
            return conversation_id
    raise HTTPException(status_code=404, detail="Invalid line.")



