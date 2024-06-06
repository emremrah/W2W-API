from typing import List

from imdb import Cinemagoer
from imdb.parser.http import IMDbHTTPAccessSystem

from wtw import caching, core
from wtw.constants import GENRES
from wtw.models import Movie

from .models import Top100Movie
from .router import router

ia: IMDbHTTPAccessSystem = Cinemagoer(accessSystem="http")  # type: ignore

cache = caching.init_cache()


@router.post("/pop100movies", response_model=List[Movie])
async def get_pop_100_movies(request: Top100Movie.Request):
    """Get most popular 100 movies from IMDb and return filtered results."""
    pop100 = core.get_pop_100_movies(
        ia,
        cache,
        request.genres,
        request.min_rating,
        request.search_in,
        request.use_ai,
        request.user_prompt,
    )
    pop100_dict = [movie.model_dump() for movie in pop100]

    return pop100_dict


@router.get("/genres", response_model=List[str])
async def get_genres():
    return sorted(list(GENRES))
