import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db


# Flaskr will have two blueprints, one for authentication and one for other
# functions. The code for each will go into a separate module.


# Create a blurprint named 'auth'. like the application object, this needs
# to know where it's defined, so __name__ is passed as the second argument.
# The url_prefix will be prepended to all the URLs associated with the
# blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')


# @bp.route associates the URL /register with the register view function
# when flask receives a request to /auth/register, it will call the register
# view and use the return value as the response

# if the user submitted the form, request.method will be 'POST'.
# in this case, start validating the input.

# request.form is a special type of dict mapping submitted form keys and
# values. the user will input their username and password.

# validate that username and passwod are not empty
# if validation succeeds, insert the new user data insto the database

# db.execute takes a SQL query with ? placeholders for any user input,
# and a tuple of values to replace the placeholders with it.
# the database library will take care of escaping the values so we
# are not vulnerable to an SQL injection attack. yay!

# for security, passwords should never be stored in raw form, instead
# generate_password_hash() is used to securely hash the password and
# that hash is stored. since this query modifies data, db.commit()
# needs to be called afterwards to save the changes.

# an sqlite3.IntegrityError will occur if the username already exists.
# this should be shown to the user as another invalidation error

# after sorting the user, they will be redirected to the login page.
# url_for() generates the URL for the login view based on its name.
# this is prefereable to writing the URL directly as it allows us to
# change the URL later without changing all code that links to it.
# redirect() generates a redirect response to the generated URL

# if validation fails, the error is shown to the user. flash()
# stores messages that can be retrieved when rendering the template

# when the user initially navigates to auth/register or there was
# a validation error, a HTML page with the registration form should
# be shown. render_template() will render a template containing the
# HTML.

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'username not provided'
        elif not password:
            error = 'password not provided'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f'user {username} is already registered'
            else:
                return redirect(url_for("auth.login"))
            
        flash(error)
    
    return render_template('auth/register.html')


# the user is queried first and stored in a variable for later use
# fetchone() returns one row from the query, if the query returned no
# results, it returns None. fetchall() will be used later on which
# returns a list of all results.

# check_password_hash() hashes the submitted password in the same way
# as the stored hash and securely compares them. if they match, the
# password is valid.

# session is a dict that stored data across requests. when validation
# succeeds, the user's id is stored in a new session. the data is
# stored in a cookie that is sent to the browser, and the browser then
# sends it back with each subsequent request. flask securely signs
# the data so that it can't be tampered with. 

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user where username = ?', (username,)
        ).fetchone()

        if user is None or not check_password_hash(user['password'], password):
            error = 'incorrect username or password'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)

    return render_template('auth/login.html')

# log in

# with the user's id stored in the session it should be available on
# subsequent requests.

# bp.before_app_request() registers a function that runs before the
# view function, no matter what URL is re-quested.
# load_logged_in_user checks if a user id is stored in the session
# and gets that user's data fro the database, storing it on g.user
# which lasts for the length of one request. if there is no user id,
# or if the id doesn't exist, g.user will be None.

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# log out

# to log out, we need to remove the user id from the session.
# then loag_logged_in_user won't load a user on subsequent requests

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# require authentication in other views

# creating, editing and deleting content will require a user to be logged in.
# a decorator can be used to check this for each view it is applied to.

# this decorator returns a new view function that wrpas the original view it
# was applied to. the new function checks if a user is loaded and redirects
# to the login page otherwise. if a user is loaded the original view is
# called and continues normally. 

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view





