import flask

import blog_mgr.auth
import blog_mgr.db

bp = flask.Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = blog_mgr.db.get()
    posts = db.execute(
        "SELECT post_id, title,time_created,first_name,last_name,user_name,description, author_id " +
        "FROM post LEFT JOIN user ON post.author_id = user.user_id NATURAL JOIN user ORDER BY time_created DESC;"
    ).fetchall()
    return flask.render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=['GET', 'POST'])
@blog_mgr.auth.login_required
def create():
    if flask.request.method == 'POST':
        content = read_post_form()

        if content['error'] is not None:
            flask.flash(content['error'])
        else:
            db = blog_mgr.db.get()
            db.execute(
                'INSERT INTO post(title, body, author_id, description)'
                'VALUES(?, ?, ?, ?)',
                (content['title'], content['body'],
                 flask.g.user['user_id'], content['description'])
            )
            db.commit()
            return flask.redirect(flask.url_for('blog.index'))

    return flask.render_template('blog/create.html')


def get_post(post_id, check_author=True):
    post = blog_mgr.db.get().execute(
        "SELECT post_id, body, title,time_created,first_name,last_name,user_name,description, user_id, author_id " +
        "FROM post LEFT JOIN user ON post.author_id = user.user_id NATURAL JOIN user WHERE post_id = ?;",
        (post_id,)
    ).fetchone()
    if post is None:
        flask.abort(404, f"Post id '{post_id}' does not exist.")

    if check_author:
        if post['user_id'] != flask.g.user['user_id']:
            flask.abort(403)

    return dict(post)


def read_post_form():
    title = flask.request.form['title']
    body = flask.request.form['body']
    description = flask.request.form['description']

    error = None
    if not title:
        error = 'Title is required'
    if not body:
        error = 'Body is required'

    return {"title": title, "body": body, "description": description, "error": error}


@bp.route('/view/<int:post_id>')
def view(post_id: int):
    db = blog_mgr.db.get()
    post = get_post(post_id, check_author=False)

    return flask.render_template('blog/viewer.html', post=post)


@bp.route('/update/<int:post_id>', methods=['GET', 'POST'])
@blog_mgr.auth.login_required
def update(post_id: int):
    post = get_post(post_id)

    if flask.request.method == 'POST':
        content = read_post_form()
        if content['error'] is not None:
            flask.flash(content['error'])
        else:
            db = blog_mgr.db.get()
            db.execute(
                'UPDATE post SET title = ?, body = ?, description = ? WHERE post_id = ?',
                (content['title'], content['body'],
                 content['description'], post_id)
            )
            db.commit()
            return flask.redirect(flask.url_for('blog.index'))
    return flask.render_template('blog/update.html', post=post)


@bp.route('/delete/<int:post_id>', methods=['POST'])
@blog_mgr.auth.login_required
def delete(post_id):
    # don't really care about what the post is, but want to check 
    # if the user is allowed to modify the post
    _ = get_post(post_id)

    db = blog_mgr.db.get()
    db.execute('DELETE FROM post WHERE post_id = ?', (post_id,))
    db.commit()

    return flask.redirect(flask.url_for('blog.index'))


@bp.route('/user/<handle>')
def view_user(handle):
    if handle[0] != '@':
        flask.abort(404, f"Handles must begin with '@' symbol")

    user_name = handle[1:]

    db = blog_mgr.db.get()
    user = db.execute('SELECT user_id, first_name, last_name, user_name FROM user WHERE user_name = ?',
                      (user_name,)).fetchone()
    user_posts = db.execute(
        "SELECT post_id, title,time_created,description, user_name, author_id " +
        "FROM post LEFT JOIN user ON post.author_id = user.user_id NATURAL JOIN user user WHERE user.user_name = ? "
        "ORDER BY time_created DESC;",
        (user_name,)
    ).fetchall()

    list = [dict(post) for post in user_posts]

    return flask.render_template('blog/view_user.html', user=user, posts=list)
