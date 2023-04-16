import sqlite3

# g is a special object that is unique for each request. it is used to
# store data that might be accessed by multiple funcitons during the request.
# the connection is stored and reused instead of creating a new connection if
# get_db() is called a second time in the same request

# current_app is another special object that points to the Flask application
# handling the request. since we used an application factory, there is no
# application object when writing the rest of our code. get_db() will be
# called when the application has been created and is handling a request so
# current_app can be used

# sqlite3.connect() creates a connection to the file pointed at by the DATABASE
# configuration key. this file does not have to exist yet, and won't until we
# initialise the database later

# sqlite3.Row tells the connection to return rows that behave like dicts. This
# allows accessing the columns by name.

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    
    return g.db


# close_db() checks if a connection wa screated by checking if g.db was set.
# if connection exists, it is closed.

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# open_resource() opens a file relative to the flaskr package which is useful
# since we won't necessarily know where that location is when deploying the
# application.
# get_db() returns a database connection which is used to execute the commands
# read from the file

# click.command() defines a line command called init-db that calls the init_db
# function and shows a success message

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """clear the existing data and create new tables"""
    init_db()
    click.echo('initialised the database')

# the close_db and init_db_command functions need to be registered with the
# application instance, so the application know's they exist.
# Since we are using a factory function, the instance isn't available when
# writing the functions, so instead we write a function that takes an
# application and automatically does the registration

# app.teardown_appcontext() tells flask to call that function when cleaning up
# after returning the response.

# app.cli.add_command() adds a new command that can be called with the
# flask command, so we can call init_db_command()

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


