from typing import Dict, List

from flask import jsonify, request
from imdb import Cinemagoer
from imdb.Movie import Movie
from imdb.parser.http import IMDbHTTPAccessSystem

from wtw.caching import cache
from wtw.constants import GENRES
from wtw.core import get_pop_100_list
from wtw.models import MovieModel, Top100Request
from wtw.movies import get_movie

from . import create_app

app = create_app()

ia: IMDbHTTPAccessSystem = Cinemagoer(accessSystem='http')  # type: ignore


def check_rating(movie: Movie, min_rating: float):
    """Return if a movie's rating is below given minimum rating."""
    if movie.get('rating', 0) < min_rating:
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
        movie_genres = movie.get('genres', [])
        movie_genres = [genre.lower() for genre in movie_genres]

        # filter movie
        if not any([genre.lower() in movie_genres for genre in genres]):
            continue
        matched_movies.append(movie)

    return matched_movies


def get_pop_100(genres: List[str], min_rating: float, search_in: int):
    """
    Get most popular 100 movies from IMDb and filter the results.

    Arguments
    ---------
    genres: the list of genre names to filter movies that doesn't have any of
    them
    min_rating: the minimum rating a movie can have
    search_in: search in maximum number of # movies

    """
    filtered_movies: List[Dict] = []
    # get 100 most popular movies
    pop100 = get_pop_100_list(ia, cache)

    # limit in top # of movies
    pop100 = pop100[:search_in]

    # filter movies by rating before fetching genres data
    pop100 = [movie for movie in pop100 if check_rating(movie, min_rating)]

    # get additional info for the movies
    pop100 = [get_movie(movie.movieID, ia, cache) for movie in pop100]

    pop100 = filter_genres(pop100, genres)

    for movie in pop100:
        movie = MovieModel(id=movie.getID(),
                           title=movie.get('title'),
                           plot=movie.get('plot outline', ''),
                           rating=movie.get('rating'),
                           genres=movie.get('genre', []))
        filtered_movies.append(movie.dict())

    return filtered_movies


@app.route('/pop100', methods=['POST'])
def get_top_100():
    """Get most popular 100 movies from IMDb and return filtered results."""
    req = Top100Request.Request(**request.get_json())

    pop100 = get_pop_100(req.genres, req.min_rating, req.search_in)

    return jsonify(pop100)


@app.route('/genres', methods=['GET'])
def get_genres():
    return jsonify(sorted(list(GENRES)))
