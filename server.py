"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template('homepage.html')


@app.route('/users')
def user_list():
    """Show a list of all users"""

    users = User.query

    return render_template('user_list.html',
                           log_status=set_log_status(), users=users)


@app.route('/users/<user_id>')
def show_user_info(user_id):
    """Display user info page"""

    if not user_id.isdigit():
        flash('User does not exist')
        return redirect('/')

    user = User.query.get(user_id)

    if not user:
        flash('User does not exist')
        return redirect('/')

    user_ratings = db.session.query(Movie.title,
                                    Rating.score).join(Rating).filter_by(
                                    user_id=user_id).all()

    return render_template('user_info.html',
                           user=user, user_ratings=user_ratings)


@app.route('/register')
def show_register_form():
    """Show the register user form"""

    return render_template('register.html')


@app.route('/register', methods=['POST'])
def create_user():
    """Check if user exists and adds new users to database"""

    email = request.form.get('email')
    password = request.form.get('password')
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')
    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email taken')
        return redirect('/register')

    new_user = User(email=email, password=password, age=age, zipcode=zipcode)
    db.session.add(new_user)
    db.session.commit()

    flash('Created new user')

    return redirect('/login')


@app.route('/login')
def show_login_form():
    """Show login form page"""

    return render_template('login_form.html')


@app.route('/login', methods=['POST'])
def perform_login():
    """Process login information"""

    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if not user or user.password != password:
        flash('Invalid login')
        return redirect('/login')

    session['user_id'] = user.user_id

    flash('Successfully logged in')

    return redirect(f'/users/{user.user_id}')


@app.route("/logout")
def log_out_user():
    """Log out the user and flash a message if successful"""

    session.pop('user_id', None)
    flash('Logged out')

    return redirect('/')


@app.route('/movies')
def list_all_movies():
    """Show a list of all movies"""

    movies = Movie.query.order_by('title').all()

    return render_template('movie_list.html',
                           log_status=set_log_status(), movies=movies)


@app.route('/movies/<movie_id>')
def show_movie_info(movie_id):
    """Display movie info page"""

    if not movie_id.isdigit():
        flash('Movie does not exist')
        return redirect('/')

    movie = Movie.query.get(movie_id)

    if not movie:
        flash('Movie does not exist')
        return redirect('/')

    movie_ratings = db.session.query(Rating.user_id, Rating.score).filter_by(
                    movie_id=movie.movie_id).all()

    return render_template('movie_info.html',
                           movie=movie, movie_ratings=movie_ratings)


@app.route('/movies/<movie_id>', methods=['POST'])
def set_movie_rating(movie_id):
    """Set movie rating"""

    user_id = session.get('user_id')
    score = request.form.get("rating")

    this_rating = Rating.query.filter_by(user_id=user_id,
                                         movie_id=movie_id).first()

    if this_rating:
        this_rating.score = score
    else:
        this_rating = Rating(user_id=user_id, movie_id=movie_id, score=score)
        db.session.add(this_rating)

    db.session.commit()

    return redirect(f'/movies/{movie_id}')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
