from model import User, Rating, Movie, connect_to_db, db
from correlation import pearson
from flask_sqlalchemy import SQLAlchemy
from math import sqrt
from server import app

db = SQLAlchemy()


connect_to_db(app)


def make_movie_rating_dict(user):
    """Create a dict with movie_id as a key and score as value"""

    rating_dict = {}

    for rating in user.ratings:
        rating_dict[rating.movie_id] = rating.score

    return rating_dict


def make_paired_ratings(wanted_user, other_user):
    """Create list of tuples of ratings for the same movie and return list"""

    user_rating = make_movie_rating_dict(wanted_user)
    other_rating = make_movie_rating_dict(other_user)
    paired_ratings = []

    for movie in user_rating:
        if movie in other_rating:
            paired_ratings.append((user_rating[movie], other_rating[movie]))

    return paired_ratings


def calc_pearson_corr(wanted_user, other_users):
    """Takes wanted user and list of other users and returns correlation"""

    correlations = []

    for other_user in other_users:
        pairs = make_paired_ratings(wanted_user, other_user)
        if pairs:
            correlation = pearson(pairs)
            correlations.append((other_user, correlation))

    return correlations


# run math to compare tuples
# add comparason score and user_id to a list

u_196 = User.query.get(196)
kolya = Movie.query.get(242)
other_users = kolya.users
u_196_kolya_correlations = calc_pearson_corr(u_196, other_users)

print(u_196_kolya_correlations[15:100])
