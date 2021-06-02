from typing import Dict, List

import diskcache as dc
from flask import jsonify, request
from imdb import IMDb
from imdb.Movie import Movie

from wtw.assets.genres import GENRES

from . import create_app
from .models import MovieModel, Top100Request

app = create_app()
cache = dc.Cache('./tmp')

ia = IMDb()

MOVIE_EXPIRE = 1 * 60 * 60 * 24  # a day
POP100_EXPIRE = 1 * 60 * 60 # an hour


def check_rating(movie: Movie, min_rating: float):
    """Return if a movie's rating is below given minimum rating."""
    if movie.get('rating', 0) < min_rating:
        return False
    return True


def get_movies(movies: List[Movie], use_cache: bool = True):
    """
    Get additional data for movies.

    For a given list of movies, get additional genres and plot information for
    them and return a new list of movies."""
    updated_movies: List[Movie] = []

    for movie in movies:
        movie_id = movie.getID()

        # check if movie is already in cache
        if movie_id in cache and use_cache:
            updated_movies.append(cache[movie.getID()])
            # update expire date
            cache.touch(movie_id)
        else:
            movie = ia.get_movie(
                movie_id, info=['main', 'plot', 'genres'])
            updated_movies.append(movie)
            cache.set(movie_id, movie, expire=MOVIE_EXPIRE)

    return updated_movies


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
    if 'pop100' in cache:
        pop100 = cache.get('pop100')
    else:
        pop100: List[Movie] = ia.get_popular100_movies()
        cache.set('pop100', pop100, expire=POP100_EXPIRE)  # expire in a hour

    # limit in top # of movies
    pop100 = pop100[:search_in]

    # filter movies by rating before fetching genres data
    pop100 = [movie for movie in pop100 if check_rating(movie, min_rating)]

    # get additional info for the movies
    pop100 = get_movies(pop100)

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
    return jsonify(sorted(list(GENRES.keys())))
