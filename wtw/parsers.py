import imdb.Movie

from wtw.models import Movie


def parse_imdb_movie(imdb_movie: imdb.Movie.Movie):
    try:
        title = imdb_movie["title"]
    except KeyError:
        raise ValueError("Movie does not have a title")

    if not isinstance(title, str):
        raise ValueError("Movie title must be a string")

    genres = imdb_movie.get("genres", [])
    if not isinstance(genres, list):
        raise ValueError("Movie genres must be a list")

    imdb_plot = imdb_movie.get("plot", None)
    if imdb_plot is not None and isinstance(imdb_plot, list):
        try:
            plot = imdb_plot[0]
        except IndexError:
            plot = None

    return Movie(
        id=imdb_movie.movieID,
        title=title,
        plot=plot,
        genres=genres,
        rating=imdb_movie.get("rating", None),
        image_url=imdb_movie.get("cover url", None),
        imdb_url=imdb_movie.get("imdb url", None),
    )
