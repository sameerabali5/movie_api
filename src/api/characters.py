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
        """Function returns the list of characters that the
        character has the most conversations with,
        sorted by number of lines together """
        # access conversations database
        conversations = db.conversations

        # map that points each character to all their conversationIDs
        map = {}

        # iterate through conversations to find list of characters
        # that have conversations
        for conversation in conversations:
            if conversations[conversation]["movie_id"] == movieID:
                char1id = conversations[conversation]["character1_id"]
                char2id = conversations[conversation]["character2_id"]
                if char1id == charID:
                    other_char = conversations[conversation]["character2_id"]
                elif char2id == charID:
                    other_char = conversations[conversation]["character1_id"]
                else:
                    continue
                # append character_id and conversation to map
                if other_char not in map:
                    map.setdefault(other_char, []).append(conversation)
                else:
                    map[other_char].append(conversation)

        characters = db.characters
        lines = db.lines
        json = []

        # iterate through character_ids in map and creates json
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

    # accessing databases for results
    characters = db.characters
    movies = db.movies

    # generates json with queried character along with the characters within movie
    if id in characters:
        top_convos = top_conversations(id, characters[id]["movie_id"])
        movie_id = characters[id]["movie_id"]
        return {
            "character_id": int(id),
            "character": characters[id]["name"],
            "movie": movies[movie_id]["title"],
            "gender": (characters[id]["gender"] or None),
            "top_conversations": sorted(top_convos, key=lambda x:
            (-x["number_of_lines_together"], x["character"]))
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
    sortedCharacters = db.sortedCharacters
    sortedMovies = db.sortedMovies
    sortedLines = db.sortedLines
    movies = db.movies
    lst = []

    if sort == character_sort_options.character:
        lst = sortedCharacters
    if sort == character_sort_options.movie:
        lst = sortedMovies
    if sort == character_sort_options.number_of_lines:
        lst = sortedLines

    if name != "":
        if sort == "character" or sort == "movie":
            lst = list(filter(lambda x: name.lower() in x["name"].lower(), lst))

    json = []
    for dict in lst:
        if sort == character_sort_options.number_of_lines:
            charId = dict[0]
            movie_id = dict[1]
            charname = list(filter(lambda x: x['character_id'] == charId,
                                   sortedCharacters))[0]["name"]
            number_of_lines = lst[dict]
        else:
            charId = dict["character_id"]
            movie_id = dict["movie_id"]
            charname = dict["name"]
            number_of_lines = sortedLines[(charId, movie_id)]
        x = {
            "character_id": int(charId),
            "character": charname,
            "movie": movies[movie_id]["title"],
            "number_of_lines": number_of_lines
        }
        if len(json) < limit:
            if sort == "number_of_lines":
                if name and name.lower() in charname.lower():
                    json.append(x)
            else:
                json.append(x)
        else:
            break
    json = json[offset: len(json)]
    return json

