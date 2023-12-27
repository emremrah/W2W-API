from typing import List

from diskcache import Cache
from imdb.Movie import Movie
from imdb.parser.http import IMDbHTTPAccessSystem

from wtw.config import POP100_EXPIRE


def get_pop_100_list(ia: IMDbHTTPAccessSystem, cache: Cache):
    if "pop100" in cache:
        pop100 = cache.get("pop100")
    else:
        pop100: List[Movie] = ia.get_popular100_movies()
        cache.set("pop100", pop100, expire=POP100_EXPIRE)
    return pop100
