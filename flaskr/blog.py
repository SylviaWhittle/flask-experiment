from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


# update and delete views will need to fetch a post by id and check if
# the author matches the logged in user. to avoid duplicaiton, we
# can write a function to get the post and call it from each view

# abort() will raise a special exception that returns a HTTP status
# code. it takes an optional message to show with the error,
# otherwise a default message is used. 404 means not found, and 
# 403 means forbidden. 

# the check_author argument is defined so that the function
# can be used to get a post without checking the author.
# this would be useful if we write a view to show an
# individual post on a page, where the user doesn't
# matter because they're not modifying the post.

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id=?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"post id {id} does not exist")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

# the index will show all of the posts, most recent first.
# a JOIN is used so that the author information from the
# user table is available in the result.

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
# @login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'title is required'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                'VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')

# unlike the other views, the update function takes an argument, id
# this corresponds to the <int:id> in the route. a real url will look
# like /1/update. Flask will capture the 1, ensure it's an integer, and
# pass it as the id argument. if we don't specify int: and instead do
# <id>, it will be a string. to generate a URL to the update page,
# url_for() needs to be passed the id so it knows what to fill in:
# url_for('blog.update, id=post['id']). this is also in the
# index.html file.

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'title is required'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/update.html', post=post)

# the delete view doesn't have its own template, the delete button is part of update.html
# and posts to the /<id>/delete URL. since there is no template, it will only handle the
# POST method and then redirect to the index view.

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
    

