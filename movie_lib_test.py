from movie_lib import *


model = MovieLens(RATINGS_PATH, MOVIES_PATH)


def test_same_user(model):
    assert model.compare_users(1, 1) == 20.0
    assert model.compare_users(1, 1) == 1 * len(model.ratings[1])

# euclidean distance weighted by movies in common ^^vv
def test_some_similarity(model):
    assert model.compare_users(1, 73) == 2.255135881683525


def test_user_zero_equality(model):
    assert model.compare_users(1, 2) == 0.0


def test_user_movie_overlap(model):
    assert model.shared_ratings(1, 4) == {1953: (4.0, 5.0), 2193: (2.0, 3.0),
                                        2968: (1.0, 5.0), 2105: (4.0, 4.0),
                                        1371: (2.5, 4.0)}


def test_similar_users(model):
    assert model.similar_users(1, 3) == [(468, 3.045189340712464), (580, 2.756021814145972), (73, 2.255135881683525)]


def test_similar_returns_list(model):
    type(model.similar_users(1, 3)) == list


def test_not_similar(model):
    similar_users = model.similar_users(1)
    assert 2 not in similar_users


test_same_user(model)
test_similar_returns_list(model)
test_user_zero_equality(model)
test_user_movie_overlap(model)
test_similar_users(model)
test_not_similar(model)
