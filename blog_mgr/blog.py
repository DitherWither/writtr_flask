import flask

import blog_mgr.auth
import blog_mgr.db

bp = flask.Blueprint('blog', __name__)


@bp.route('/')
def index():
    cursor = blog_mgr.db.get().cursor()
    posts = []

    posts = cursor.execute(
        "SELECT post_id, title,time_created,first_name,last_name,user_name,description, author " +
        "FROM posts LEFT JOIN users AS u ON author = u.user_name NATURAL JOIN users ORDER BY time_created DESC;"
    ).fetchall()
    cursor.close()
    return flask.render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=['GET', 'POST'])
@blog_mgr.auth.login_required
def create():
    if flask.request.method == 'POST':
        content = read_post_form()

        if content['error'] is not None:
            flask.flash(content['error'])
        else:
            cursor = blog_mgr.db.get().cursor()
            cursor.execute(
                'INSERT INTO posts(title, body, author, description)'
                'VALUES(%s, %s, %s, %s)',
                (content['title'], content['body'],
                 flask.g.user['user_name'], content['description'])
            )
            cursor.close()
            return flask.redirect(flask.url_for('blog.index'))

    return flask.render_template('blog/create.html')


def get_post(post_id, check_author=True):
    cursor = blog_mgr.db.get().cursor()
    post = cursor.execute(
        "SELECT post_id, body, title,time_created,first_name,last_name,user_name,description, author " +
        "FROM posts LEFT JOIN users u ON posts.author = u.user_name NATURAL JOIN users WHERE post_id = %s;",
        (post_id,)
    ).fetchone()
    cursor.close()
    if post is None:
        flask.abort(404, f"Post id '{post_id}' does not exist.")

    if check_author:
        if post['user_name'] != flask.g.user['user_name']:
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
            cursor = blog_mgr.db.get().cursor()
            cursor.execute(
                'UPDATE posts SET title = %s, body = %s, description = %s WHERE post_id = %s',
                (content['title'], content['body'],
                 content['description'], post_id)
            )
            cursor.close()
            return flask.redirect(flask.url_for('blog.index'))
    return flask.render_template('blog/update.html', post=post)


@bp.route('/delete/<int:post_id>', methods=['POST'])
@blog_mgr.auth.login_required
def delete(post_id):
    # don't really care about what the post is, but want to check
    # if the user is allowed to modify the post
    _ = get_post(post_id)

    cursor = blog_mgr.db.get().cursor()
    cursor.execute('DELETE FROM posts WHERE post_id = %s', (post_id,))
    cursor.close()

    return flask.redirect(flask.url_for('blog.index'))


@bp.route('/user/<handle>')
def view_user(handle):
    start = 0
    if handle[0] == '@':
        start = 1

    user_name = handle[start:]

    cursor = blog_mgr.db.get().cursor()
    user = cursor.execute('SELECT first_name, last_name, user_name FROM users WHERE user_name = %s',
                          (user_name,)).fetchone()
    user_posts = cursor.execute(
        "SELECT post_id, title,time_created,description, user_name, author " +
        "FROM posts LEFT JOIN users AS u ON posts.author = u.user_name NATURAL JOIN users WHERE users.user_name = %s "
        "ORDER BY time_created DESC;",
        (user_name,)
    ).fetchall()
    cursor.close()

    list = [dict(post) for post in user_posts]

    return flask.render_template('blog/view_user.html', user=user, posts=list)
