import functools
import psycopg

import flask
import werkzeug.security as security

import blog_mgr.db

bp = flask.Blueprint('auth', __name__, url_prefix="/auth")


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        user_name = flask.request.form['user_name']
        password = flask.request.form['password']
        first_name = flask.request.form['first_name']
        last_name = flask.request.form['last_name']

        error = None

        if not user_name:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif not first_name:
            error = 'First Name is required'
        elif not last_name:
            error = 'Last Name is required'

        if error is None:
            try:
                cursor = blog_mgr.db.get().cursor()
                cursor.execute(
                    "INSERT INTO users (first_name, last_name, user_name, password) VALUES (%s, %s, %s, %s)",
                    (first_name, last_name, user_name,
                     security.generate_password_hash(password))
                )
                cursor.close()
            except psycopg.IntegrityError:
                error = f"User '{user_name}' already exists"
            else:
                
                return flask.redirect(flask.url_for("auth.login"))

        flask.flash(error)

    return flask.render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        user_name = flask.request.form['user_name']
        password = flask.request.form['password']

        cursor = blog_mgr.db.get().cursor()
        error = None

        user = cursor.execute(
            "SELECT * FROM users WHERE user_name = %s", (user_name,)).fetchone()
        cursor.close()
        if user is None:
            error = 'Incorrect username'
        elif not security.check_password_hash(user['password'], password):
            error = 'Incorrect password'

        if error is None:
            flask.session.clear()
            flask.session['user_name'] = user['user_name']
            return flask.redirect(flask.url_for('blog.index'))

        flask.flash(error)

    return flask.render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_name = flask.session.get('user_name')
    if user_name is None:
        flask.g.user = None
    else:
        cursor = blog_mgr.db.get().cursor()
        flask.g.user = cursor\
            .execute('SELECT * FROM users WHERE user_name = %s', (user_name,)) \
            .fetchone()


@bp.route('logout')
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for('blog.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if flask.g.user is None:
            return flask.redirect('/auth/login')
        return view(**kwargs)

    return wrapped_view
