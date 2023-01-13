import sqlite3
import click
import flask


def get() -> sqlite3.Connection:
    if 'db' not in flask.g:
        flask.g.db = sqlite3.connect(
            flask.current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        flask.g.db.row_factory = sqlite3.Row
    return flask.g.db


def close(e=None):
    db = flask.g.pop('db', None)
    if db is not None:
        db.close()


def init():
    db = get()
    with flask.current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_command():
    init()
    click.echo("Initialized the database")


def init_app(app):
    app.teardown_appcontext(close)
    app.cli.add_command(init_command)
