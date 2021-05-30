import imdb
from wtw.app import filter_top100

ia = imdb.IMDb()


class TestTop100:
    # The Dark Knight
    test_id = '0468569'
    test_movie = ia.get_movie(test_id)
    test_movies = [test_movie]

    def test_genres(self):
        movies = filter_top100(self.test_movies, 5, ['Drama'])
        assert len(movies)

        movies = filter_top100(self.test_movies, 5, ['Comedy'])
        assert not len(movies)

    def test_rating(self):
        movies = filter_top100(self.test_movies, 5, ['Drama'])
        assert len(movies)

        movies = filter_top100(self.test_movies, 10, ['Drama'])
        assert not len(movies)

    def test_search_in(self):
        movies = filter_top100(self.test_movies, 5, ['Drama'], 5)
        assert len(movies)

        movies = filter_top100(self.test_movies, 5, ['Drama'], 0)
        assert not len(movies)
