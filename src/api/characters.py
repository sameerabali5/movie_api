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
    def get_lines(value):
        lines = db.lines
        totalLines = 0
        for line in lines:
            for val in value:
                if line["conversation_id"] == val:
                    totalLines += 1
        return totalLines
    def get_character_info(characterMap):
        keys = list(characterMap.keys())
        characters = db.characters
        json = []
        for key in keys:
            gender = list(filter(lambda x: x["character_id"] == key, characters))[0]["gender"]
            json.append(
                {
                    "character_id": int(key),
                    "character": list(filter(lambda x: x["character_id"] == key, characters))[0]["name"],
                    "gender": gender if gender != "" else None,
                    "number_of_lines_together": get_lines(characterMap.get(key))
                }
            )
        return json
    def assign_conversations(charId, movieId):
        conversations = db.conversations
        characterMap = {}
        for conversation in conversations:
            if conversation["movie_id"] == movieId:
                # check for union of both character ids
                if conversation["character1_id"] == charId:
                    if conversation["character2_id"] not in characterMap:
                        characterMap.setdefault(conversation["character2_id"], []).append(conversation["conversation_id"])
                    else:
                        characterMap[conversation["character2_id"]].append(conversation["conversation_id"])
                if conversation["character2_id"] == charId:
                    if conversation["character1_id"] not in characterMap:
                        characterMap.setdefault(conversation["character1_id"], []).append(conversation["conversation_id"])
                    else:
                        characterMap[conversation["character1_id"]].append(conversation["conversation_id"])
        return get_character_info(characterMap)

    characters = db.characters
    movies = db.movies
    for character in characters:
        if character["character_id"] == id:
            top_convos = assign_conversations(character["character_id"], character["movie_id"])
            return {
                "character_id": int(character["character_id"]),
                "character": character["name"],
                "movie": list(filter(lambda x: x["movie_id"] == character["movie_id"], movies))[0]["title"],
                "gender": character.get("gender") if character.get("gender") != "" else None,
                "top_conversations": sorted(top_convos, key=lambda x: x["number_of_lines_together"], reverse=True)
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

    def get_conversations(charID, movieID):
        """Given character ID and movie ID, returns the number of lines
        the character has in that movie"""
        res = []
        for line in db.lines:
            if charID == line["character_id"] and movieID == line["movie_id"]:
                res.append(line)
        return len(res)

    # accessing characters and movies database
    characters = db.characters
    movies = db.movies

    # filter for characters whose name contains a string
    if name:
        characters = list(filter(lambda x: name.lower() in x["name"].lower(), characters))

    # json is an endpoint of list of characters with required information
    json = []
    for character in characters:
        json.append({
            "character_id": int(character["character_id"]),
            "character": character["name"],
            "movie": list(filter(lambda x: x["movie_id"] == character["movie_id"],
                                 movies))[0]["title"],
            "number_of_lines": get_conversations(character["character_id"], character["movie_id"])
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
