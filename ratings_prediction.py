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
            correlations.append((other_user.user_id, correlation))

    return correlations


def predict_rating(movie_id, correlation_info):
    """Gets predicted score based on correlated users"""

    pos = 0
    neg = 0
    denominator = 0

    for user_id, correlation in correlation_info:
        user_score = Rating.query.filter_by(user_id=user_id,
                                            movie_id=movie_id).one().score
        if correlation > 0:
            pos += (correlation * user_score)

        else:
            neg += (-(correlation) * abs(user_score - 6))

        denominator += abs(correlation)

    return (pos + neg)/denominator


def run_prediction(movie, wanted_user):
    """Create a predicted rating given movie and user"""

    other_users = movie.users

    if wanted_user in other_users:
        other_users.remove(wanted_user)

    correlation_list = calc_pearson_corr(wanted_user, other_users)

    return predict_rating(movie.movie_id, correlation_list)


wanted_user = User.query.get(166)
movie = Movie.query.get(346)
print(run_prediction(movie, wanted_user))
