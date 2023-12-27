from imdb import Cinemagoer

from wtw.api.app import check_rating, filter_genres

ia = Cinemagoer()


class TestTop100:
    # The Dark Knight
    test_id = '0468569'
    test_movie = ia.get_movie(test_id)
    # test_movies = get_movie(test_movie.movieID, ia, None)

    def test_genres(self):
        movies = filter_genres([self.test_movie], ['Drama'])
        assert len(movies)

        movies = filter_genres([self.test_movie], ['Comedy'])
        assert not len(movies)

    def test_rating(self):
        assert check_rating(self.test_movie, 5)

        assert not check_rating(self.test_movie, 10)
