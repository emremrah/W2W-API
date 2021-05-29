from typing import List

from flask import jsonify, request
from imdb import IMDb
from imdb.Movie import Movie

from . import create_app
from .models import MovieModel, Top100Request

app = create_app()

ia = IMDb()


def filter_top100(top100: List[Movie], min_rating: int, genres: List[str], search_in: int = 100):
    edible_movies = []

    # limit the number of movies to be searched by zipping the loop
    for _, movie in zip(range(search_in), top100):
        movie: Movie = ia.get_movie(movie.getID(), info=('main', 'genre'))

        movie_genres = [genre.lower()
                        for genre in movie.get('genre') if genre is not None]

        # if any of the user's desired genres are not in the movie's, skip this
        # movie
        if not any([genre.lower() in movie_genres for genre in genres]):
            continue

        # if movie's rating is below minimum rating, skip this movie
        if movie.get('rating', 0) < min_rating:
            continue

        # create a movie model and add it to "edible" movie list
        movie = MovieModel(id=movie.getID(),
                           title=movie.get('title'),
                           plot=movie.get('plot'),
                           rating=movie.get('rating'),
                           genres=movie.get('genre'))
        edible_movies.append(movie.dict())

    return edible_movies


@app.route('/pop100', methods=['POST'])
def get_top_100():
    req = Top100Request.Request(**request.get_json())

    # get 100 most popular movies
    top100: List[Movie] = ia.get_popular100_movies()

    edible_movies = filter_top100(
        top100, req.min_rating, req.genres, req.search_in)
    return jsonify(edible_movies)
