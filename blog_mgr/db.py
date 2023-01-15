import psycopg
import os
import click
import flask


def get():
    # return connection
    if 'db' not in flask.g:
    #     # flask.g.db = sqlite3.connect(
    #     #     flask.current_app.config["DATABASE"],
    #     #     detect_types=sqlite3.PARSE_DECLTYPES
    #     # )
    #     # flask.g.db.row_factory = sqlite3.Row
        flask.g.db = psycopg.connect(os.environ.get('DATABASE_URL'), row_factory=psycopg.rows.dict_row)
        print(flask.g.db)

    return flask.g.db


def close(e=None):
    db = flask.g.pop('db', None)
    if db is not None:
        db.commit()
        db.close()


def init():
    db = get()
    cursor = db.cursor()
    with flask.current_app.open_resource('schema.sql') as f:
        cursor.execute(f.read().decode('utf8'))

    # Do not try to sanitize the "input", will cause it to fail.
    # Doing so will escape the username and cause a syntax error.
    # The "input" is coming from the .env file anyways.
    # cursor.execute(
    #     f"ALTER TABLE users OWNER TO {os.environ.get('POSTGRESQL_USER')}")
    # cursor.execute(
    #     f"ALTER TABLE posts OWNER TO { os.environ.get('POSTGRESQL_USER') }")

    cursor.close()


@click.command('init-db')
def init_command():
    init()
    click.echo("Initialized the database")


def init_app(app):
    app.teardown_appcontext(close)
    app.cli.add_command(init_command)
