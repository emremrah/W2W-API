from typing import List, Optional

from imdb.Movie import Movie
from imdb.parser.http import IMDbHTTPAccessSystem

from wtw import models
from wtw.ai.assistant import CustomAssistant
from wtw.caching import Cache
from wtw.config import POP100_EXPIRE
from wtw.constants import IMDB_MOVIE_URL
from wtw.movies import get_movie
from wtw.parsers import parse_imdb_movie
from wtw.scrapers.fetch import get_pop_movies_imdb_parser

ai_assistant = CustomAssistant()


def check_rating(movie: Movie, min_rating: float):
    """Return if a movie's rating is below given minimum rating."""
    if movie.get("rating", 0) < min_rating:
        return False
    return True


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


def get_pop_100_movies(
    ia: IMDbHTTPAccessSystem,
    cache: Optional[Cache],
    genres: List[str],
    min_rating: float,
    search_in: int,
    use_ai: bool = False,
    user_prompt: Optional[str] = None,
) -> List[models.Movie]:
    """
    Get most popular 100 movies from IMDb and filter the results.

    Arguments
    ---------
    genres: the list of genre names to filter movies that doesn't have any of
    them
    min_rating: the minimum rating a movie can have
    search_in: search in maximum number of # movies

    """
    # get most popular movies
    if cache is not None and "pop100" in cache:
        pop100_movies = cache.get("pop100", default=[])
    else:
        pop100_movies = get_pop_movies_imdb_parser(ia)
        if cache is not None:
            cache.set("pop100", pop100_movies, expire=POP100_EXPIRE)

    # limit in top # of movies
    pop100_movies: List[Movie] = pop100_movies[:search_in]

    # filter movies by rating
    pop100_movies = [
        movie for movie in pop100_movies if check_rating(movie, min_rating)
    ]

    # get additional info for the movies
    pop100_movies = [
        get_movie(movie.movieID, ia, cache) for movie in pop100_movies
    ]

    pop100_movies = filter_genres(pop100_movies, genres)

    movies = [parse_imdb_movie(movie) for movie in pop100_movies]

    # ask ai if enabled
    ai_summaries: dict = {}
    if use_ai and user_prompt:
        ai_summaries = ai_assistant.ask_for_movies(  # type: ignore
            user_prompt, genres, CustomAssistant.format_movies(movies)
        )
        # convert list of dicts to dict
        ai_summaries = {
            summary.title: summary.model_dump() for summary in ai_summaries
        } or {}

    return [
        models.Movie(
            id=movie.getID(),
            title=movie.get("title", ""),
            plot=movie.get("plot outline"),
            rating=movie.get("rating"),
            genres=movie.get("genre", []),
            image_url=movie.get_fullsizeURL(),
            imdb_url=IMDB_MOVIE_URL.format(movie.movieID),
            ai_summary=ai_summaries.get(movie.get("title"), {}).get(
                "reason_to_watch",
            ),
        )
        for movie in pop100_movies
    ]
