from imdb import Cinemagoer

from wtw.api.app import check_rating, filter_genres, get_movies

ia = Cinemagoer()


class TestTop100:
    # The Dark Knight
    test_id = '0468569'
    test_movie = ia.get_movie(test_id)
    test_movies = get_movies([test_movie], 0)

    def test_genres(self):
        movies = filter_genres(self.test_movies, ['Drama'])
        assert len(movies)

        movies = filter_genres(self.test_movies, ['Komedi'])
        assert not len(movies)

    def test_rating(self):
        assert check_rating(self.test_movie, 5)

        assert not check_rating(self.test_movie, 10)

    def test_search_in(self):
        test_movie = ia.get_movie(self.test_id)
        test_movies = [test_movie]
        test_movie = get_movies(test_movies, use_cache=False)[0]
        assert len(test_movie.get('genres'))
