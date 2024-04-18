from typing import List

from imdb import Cinemagoer
from imdb.parser.http import IMDbHTTPAccessSystem

from wtw import caching
from wtw.api.router import router
from wtw.constants import GENRES
from wtw.core import get_pop_100
from wtw.models import Top100Request

ia: IMDbHTTPAccessSystem = Cinemagoer(accessSystem="http")  # type: ignore

cache = caching.init_cache()


@router.post("/pop100movies", response_model=List[dict])
async def get_pop_100_movies(request: Top100Request.Request):
    """Get most popular 100 movies from IMDb and return filtered results."""
    pop100 = get_pop_100(
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
