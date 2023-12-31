import json
from typing import Dict, List, Optional

from imdb.Movie import Movie
from imdb.parser.http import IMDbHTTPAccessSystem

from mock.openai import ask_openai
from wtw.caching import Cache
from wtw.config import POP100_EXPIRE
from wtw.constants import IMDB_MOVIE_URL
from wtw.models import MovieModel
from wtw.movies import get_movie


def check_rating(movie: Movie, min_rating: float):
    """Return if a movie's rating is below given minimum rating."""
    if movie.get("rating", 0) < min_rating:
        return False
    return True


def get_pop_100_list(ia: IMDbHTTPAccessSystem, cache: Optional[Cache]):
    if cache is not None and "pop100" in cache:
        pop100 = cache.get("pop100")
    else:
        pop100: List[Movie] = ia.get_popular100_movies()
        cache.set("pop100", pop100, expire=POP100_EXPIRE)
    return pop100


def filter_genres(movies: List[Movie], genres: List[str]):
    """
    Filter a list of movies by comparing their genres with given list of genres.

    If any genre of a movie is not in given list of genres, filter our that
    movie."""
    matched_movies: List[Movie] = []

    for movie in movies:
        # get genres of the movie
        movie_genres = movie.get("genres", [])
        movie_genres = [genre.lower() for genre in movie_genres]

        # filter movie
        if not any([genre.lower() in movie_genres for genre in genres]):
            continue
        matched_movies.append(movie)

    return matched_movies


def get_pop_100(
    ia: IMDbHTTPAccessSystem,
    cache: Optional[Cache],
    genres: List[str],
    min_rating: float,
    search_in: int,
) -> List[MovieModel]:
    """
    Get most popular 100 movies from IMDb and filter the results.

    Arguments
    ---------
    genres: the list of genre names to filter movies that doesn't have any of
    them
    min_rating: the minimum rating a movie can have
    search_in: search in maximum number of # movies

    """
    filtered_movies: List[MovieModel] = []

    # get 100 most popular movies
    pop100_list = get_pop_100_list(ia, cache)

    # limit in top # of movies
    pop100_list = pop100_list[:search_in]

    # filter movies by rating
    pop100_list = [
        movie for movie in pop100_list if check_rating(movie, min_rating)
    ]

    # get additional info for the movies
    pop100_movies = [
        get_movie(movie.movieID, ia, cache) for movie in pop100_list
    ]

    pop100_movies = filter_genres(pop100_movies, genres)

    # ask ai
    ai_summaries: Dict = json.loads(ask_openai(
        [movie.get("title") for movie in pop100_movies]))

    for movie in pop100_movies:
        movie = MovieModel(
            id=movie.getID(),
            title=movie.get("title"),
            plot=movie.get("plot outline", ""),
            rating=movie.get("rating"),
            genres=movie.get("genre", []),
            image_url=movie.get_fullsizeURL(),
            imdb_url=IMDB_MOVIE_URL.format(movie.movieID),
            ai_summary=ai_summaries.get(
                movie.get("title"), {}).get("explanation"),
        )
        filtered_movies.append(movie)

    return filtered_movies
