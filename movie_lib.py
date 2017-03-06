import os
import csv
from datetime import datetime
from collections import defaultdict
import math
import heapq
from operator import itemgetter

RATINGS_PATH = 'ratings.csv'
MOVIES_PATH = 'movies.csv'


class MovieLens:

    def __init__(self, rating_path, movie_path):
        self.rating_path = rating_path
        self.movie_path = movie_path
        self.movies = {}
        self.ratings = defaultdict(dict)
        self.load_data()

    def load_data(self):
        for movie in load_movies(self.movie_path):
            self.movies[movie['movieId']] = movie

        for rating in load_ratings(self.rating_path):
            self.ratings[rating['userId']][rating['movieId']] = rating

    def ratings_for_movie(self, movieid):
        for rating in self.ratings.values():
            if movieid in rating:
                yield rating[movieid]

    def average_rating(self, movieId):
        ratings = [rate['rating'] for rate in self.ratings_for_movie(movieId)]
        average_rating = sum(ratings) / len(ratings)
        return "Average rating: {:0.3f} ({} ratings)".format(average_rating, len(ratings))

    def bayseian_average(self, c=11, m=3):
        for movieid in self.movies:
            ratings = [rate['rating'] for rate in self.ratings_for_movie(movieid)]
            average = ((c * m) + sum(ratings)) / (c + len(ratings))
            yield (movieid, average, len(ratings))

    def shared_ratings(self, user1, user2):
        if user1 not in self.ratings:
            raise KeyError("UserId {} not found".format(user1))
        if user2 not in self.ratings:
            raise KeyError("UserId {} not found".format(user2))

        user_ratings = {}
        movies_for_u1 = [movie for movie in self.ratings[user1].keys()]
        movies_for_u2 = [movie for movie in self.ratings[user2].keys()]

        shared_movies = set(movies_for_u1).intersection(movies_for_u2)

        for movieId in shared_movies:
            user_ratings[movieId] = (self.ratings[user1][movieId]['rating'],
                                     self.ratings[user2][movieId]['rating'],)

        return user_ratings

    def compare_users(self, user1, user2):
        '''uses Eucildean distance to compare the ratings of user1 and user2'''
        shared_movies = self.shared_ratings(user1, user2)
        if len(shared_movies) == 0:
            return 0
        sum_of_squares = sum(math.pow(u1-u2, 2) for u1,u2 in shared_movies.values())
        return 1 / (1 + math.sqrt(sum_of_squares))

    def top_rated(self, n=10):
        # heapq quickly sorts the reviews based on average
        return heapq.nlargest(n, self.bayseian_average(), key=itemgetter(1))

    def similar_users(self, user, n=None):
        if user not in self.ratings:
            raise KeyError("UserId {} not found".format(user))
        similar_users = {}
        for similar_user in self.ratings:
            if similar_user == user:
                continue
            user_comparison = self.compare_users(user, similar_user)
            if user_comparison != 0:
                similar_users[similar_user] = user_comparison
        if n:
            return heapq.nlargest(n, similar_users.items(), key=itemgetter(1))
        return similar_users


################################################################################


def load_ratings(path, **kwargs):
    categories = {'fieldnames': ('userId', 'movieId', 'rating', 'timestamp'), 'delimiter': ','}
    categories.update(kwargs)

    parse_int = lambda r, k: int(r[k])
    parse_float = lambda r, k: float(r[k])
    parse_date = lambda r, k: datetime.fromtimestamp(float(r[k]))

    with open(path, 'r') as ratings:
        reader = csv.DictReader(ratings, **categories)
        next(reader, None)
        for row in reader:
            row['userId'] = parse_int(row, 'userId')
            row['movieId'] = parse_int(row, 'movieId')
            row['rating'] = parse_float(row, 'rating')
            row['timestamp'] = parse_date(row, 'timestamp')
            yield row


def load_movies(path, **kwargs):
    categories = {'fieldnames': ('movieId', 'title', 'genre'), 'delimiter': ','}
    categories.update(kwargs)

    parser = lambda r, k: r[k].replace('|', ', ')
    parse_int = lambda r, k: int(r[k])

    with open(path, 'r') as ratings:
        reader = csv.DictReader(ratings, **categories)
        next(reader, None)
        for row in reader:
            row['movieId'] = parse_int(row, 'movieId')
            row['title'] = parser(row, 'title')
            row['genre'] = parser(row, 'genre')
            yield row


def main():
    model = MovieLens(RATINGS_PATH, MOVIES_PATH)
    print("\nWelcome to What to Watch movie recommender!")
    curr_user_id = input("Your user ID: ")

    while True:
        try:
            curr_user_id = int(curr_user_id)
            break
        except ValueError:
            curr_user_id = input("Please enter an integer: ")

    similar_users = model.similar_users(curr_user_id, 10)

    while True:
        print("\nThese users have similar tastes to you: ")
        for item in similar_users:
            print(item[0])
        print("Enter a user ID to see their recommendations or (0) for quit. ")
        user_select = input("Alternatively, enter a known user id for their recommendations: ")
        while True:
            try:
                user_select = int(user_select)
                break
            except ValueError:
                user_select = input("Please enter an integer: ")
        if user_select == 0:
            break

        movies_for_u1 = [movie for movie in model.ratings[curr_user_id]]
        movies_for_u2 = [movie for movie in model.ratings[user_select]]
        os.system('clear')
        print("You might enjoy these titles:\n")
        for movie in movies_for_u2:
            if movie in (movies_for_u2) and (movie not in movies_for_u1) and model.ratings[user_select][movie]['rating'] == 5.0:
                print(model.movies[movie]['title'])
                print(model.movies[movie].average_rating())


if __name__ == "__main__":
    main()
