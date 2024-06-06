from typing import List

from imdb.Movie import Movie
from imdb.parser.http import IMDbHTTPAccessSystem


def get_pop_movies_imdb_parser(ia: IMDbHTTPAccessSystem):
    pop100: List[Movie] = ia.get_popular100_movies()  # TODO: unify movie type
    return pop100
