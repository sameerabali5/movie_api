from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
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
    def top_conversations(charID, movieID):
        conversations = db.conversations
        map = {}
        for conversation in conversations:
            if conversations[conversation]["movie_id"] == movieID:
                if conversations[conversation]["character1_id"] == charID:
                    if conversations[conversation]["character2_id"] not in map:
                        char = conversations[conversation]["character2_id"]
                        map.setdefault(char, []).append(conversation)
                    else:
                        char = conversations[conversation]["character2_id"]
                        map[char].append(conversation)
                if conversations[conversation]["character2_id"] == charID:
                    if conversations[conversation]["character1_id"] not in map:
                        char = conversations[conversation]["character1_id"]
                        map.setdefault(char, []).append(conversation)
                    else:
                        char = conversations[conversation]["character1_id"]
                        map[char].append(conversation)

        characters = db.characters
        lines = db.lines
        json = []
        for character_id in list(map.keys()):
            json.append(
                {
                    "character_id": int(character_id),
                    "character": characters[character_id]["name"],
                    "gender": (characters[character_id]["gender"] or None),
                    "number_of_lines_together":
                        sum(1 for line in lines
                            for val in map.get(character_id)
                            if lines[line]["conversation_id"] == val)
                }
            )
        return json

    characters = db.characters
    movies = db.movies
    if id in characters:
        top_convos = top_conversations(id, characters[id]["movie_id"])
        movie_id = characters[id]["movie_id"]
        return {
            "character_id": int(id),
            "character": characters[id]["name"],
            "movie": movies[movie_id]["title"],
            "gender": (characters[id]["gender"] or None),
            "top_conversations": sorted(top_convos, key=lambda x: -x["number_of_lines_together"])
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

    # accessing characters and movies database
    characters = db.characters
    movies = db.movies
    lines = db.lines

    # filter for characters whose name contains a string
    if name:
        characters_to_remove = []
        for character_id in characters:
            if name.lower() not in (characters[character_id]["name"]).lower():
                characters_to_remove.append(character_id)
        characters = characters.copy()
        for character_id in characters_to_remove:
            del characters[character_id]

    #json is an endpoint of list of characters with required information
    json = []
    for character_id in list(characters.keys()):
        movie_id = characters[character_id]["movie_id"]
        json.append({
            "character_id": int(character_id),
            "character": characters[character_id]["name"],
            "movie": movies[movie_id]["title"],
            "number_of_lines": sum(v["character_id"] == character_id for v in lines.values())
        })

    # sort the results by using the `sort` query
    if sort == character_sort_options.character:
        for i in json:
            if i["character"] == "":
                json.remove(i)
        json = sorted(json, key=lambda x: x["character"])
    if sort == character_sort_options.movie:
        json = sorted(json, key=lambda x: x["movie"])
    if sort == character_sort_options.number_of_lines:
        json = sorted(json, key=lambda x: -x["number_of_lines"])

    # pagination limit and offset query
    json = json[offset: limit + offset]
    return json