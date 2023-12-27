from flask import jsonify, request
from imdb import Cinemagoer
from imdb.parser.http import IMDbHTTPAccessSystem

from wtw import caching
from wtw.constants import GENRES
from wtw.core import get_pop_100
from wtw.models import Top100Request

from . import create_app

app = create_app()

ia: IMDbHTTPAccessSystem = Cinemagoer(accessSystem='http')  # type: ignore

cache = caching.init_cache()


@app.route('/pop100', methods=['POST'])
def get_top_100():
    """Get most popular 100 movies from IMDb and return filtered results."""
    req = Top100Request.Request(**request.get_json())

    pop100 = get_pop_100(ia, cache, req.genres, req.min_rating, req.search_in)
    pop100 = [movie.model_dump() for movie in pop100]

    return jsonify(pop100)


@app.route('/genres', methods=['GET'])
def get_genres():
    return jsonify(sorted(list(GENRES)))
