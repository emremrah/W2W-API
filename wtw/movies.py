from typing import Iterable, Optional

from imdb.Movie import Movie
from imdb.parser.http import IMDbHTTPAccessSystem

from wtw.caching import Cache
from wtw.config import MOVIE_EXPIRE


def get_movie(
    movie_id: str,
    ia: IMDbHTTPAccessSystem,
    cache: Optional[Cache] = None,
    infoset: Iterable[str] = Movie.default_info,
) -> Movie:
    """
    Get movie data from IMDb.

    Arguments
    ---------
    movie_id: the IMDb id of the movie
    ia: IMDb object
    cache: the cache to use
    infoset: the list of info sets to get from IMDb

    """
    # check if movie is already in cache
    if cache is not None and movie_id in cache:
        movie: Movie = cache.get(movie_id)  # type: ignore
        # TODO: think about updating expire date
        # TODO: retrieve missing info sets if any
    else:
        movie = ia.get_movie(movie_id, info=infoset)
        if cache is not None:
            cache.set(movie_id, movie, expire=MOVIE_EXPIRE)

    return movie
