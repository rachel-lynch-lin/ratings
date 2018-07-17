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


def set_log_status():
    """Set log in/out button"""

    if session.get('user_id'):
        return "logout"
    else:
        return "login"


@app.route('/')
def index():
    """Homepage."""

    return render_template('homepage.html', log_status=set_log_status())


@app.route('/users/')
def user_list():
    """Show a list of all users"""

    users = User.query.all()

    return render_template('user_list.html',
                           log_status=set_log_status(), users=users)


@app.route('/register')
def show_register_form():
    """Show the register user form"""

    return render_template('register.html', log_status=set_log_status())


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

    return render_template('login_form.html', log_status=set_log_status())


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


@app.route('/users/<user_id>')
def show_user_info(user_id):
    """Display user info page"""

    user = User.query.get(user_id)
    user_ratings = db.session.query(Movie.title,
                                    Rating.score).join(Rating).filter_by(
                                    user_id=user_id).all()

    return render_template('user_info.html', log_status=set_log_status(),
                           user=user, user_ratings=user_ratings)


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
