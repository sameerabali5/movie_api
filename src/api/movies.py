from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()


# include top 3 actors by number of lines
@router.get("/movies/{movie_id}", tags=["movies"])
def get_movie(movie_id: str):
    """
    This endpoint returns a single movie by its identifier. For each movie it returns:
    * `movie_id`: the internal id of the movie.
    * `title`: The title of the movie.
    * `top_characters`: A list of characters that are in the movie. The characters
      are ordered by the number of lines they have in the movie. The top five
      characters are listed.

    Each character is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `num_lines`: The number of lines the character has in the movie.

    """
    def get_num_of_lines(charID, movieID):
        """Given character ID and movie ID, returns the number of lines the character has in that movie"""
        res = []
        for line in db.lines:
            if charID == line["character_id"] and movieID == line["movie_id"]:
                res.append(line)
        return len(res)
    def get_characters_in_movie(movieID):
        res = []
        characters = db.characters
        for character in characters:
            if character["movie_id"] == movieID:
                res.append(
                    {
                        "character_id": int(character["character_id"]),
                        "character": character["name"],
                        "num_lines": get_num_of_lines(character["character_id"], movieID)
                    }
                )
        res = sorted(res, key=lambda x: x["num_lines"], reverse=True)
        res = res[0 : 5]
        return res

    for movie in db.movies:
        if movie["movie_id"] == movie_id:
            return {"movie_id": int(movie["movie_id"]),
                    "title": movie["title"],
                    "top_characters": get_characters_in_movie(movie["movie_id"])}

    json = None
    if json is None:
        raise HTTPException(status_code=404, detail="movie not found.")

    return json

class movie_sort_options(str, Enum):
    movie_title = "movie_title"
    year = "year"
    rating = "rating"


# Add get parameters
@router.get("/movies/", tags=["movies"])
def list_movies(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: movie_sort_options = movie_sort_options.movie_title,
):
    """
    This endpoint returns a list of movies. For each movie it returns:
    * `movie_id`: the internal id of the movie. Can be used to query the
      `/movies/{movie_id}` endpoint.
    * `movie_title`: The title of the movie.
    * `year`: The year the movie was released.
    * `imdb_rating`: The IMDB rating of the movie.
    * `imdb_votes`: The number of IMDB votes for the movie.

    You can filter for movies whose titles contain a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `year` - Sort by year of release, earliest to latest.
    * `rating` - Sort by rating, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    movies = db.movies
    if name:
        movies = list(filter(lambda x: name.lower() in x["title"].lower(), movies))

    json = []
    for movie in movies:
        json.append(
            {
                "movie_id": int(movie["movie_id"]),
                "movie_title": movie["title"],
                "year": movie["year"],
                "imdb_rating": float(movie["imdb_rating"]),
                "imdb_votes": int(movie["imdb_votes"])
            }
        )
    if sort == movie_sort_options.movie_title:
        json = sorted(json, key=lambda x: x["movie_title"])
    if sort == movie_sort_options.year:
        json = sorted(json, key=lambda x: x["year"])
    if sort == movie_sort_options.rating:
        json = sorted(json, key=lambda x: x["imdb_rating"], reverse=True)
    json = json[offset: limit + offset]
    return json
