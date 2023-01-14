import os
from os import environ;
import dotenv

from flask import Flask
from flaskext.markdown import Markdown

import blog_mgr.auth
import blog_mgr.blog
import blog_mgr.db
from blog_mgr.blog import bp


def create_app(test_config=None):
    dotenv.load_dotenv(dotenv.find_dotenv())
    # Create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=environ.get('SECRET_KEY'),
    )
    
    if test_config is None:
        # Load the instance config if exists
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Otherwise, just load the argument passed in
        app.config.from_mapping(test_config)

    try:
        # The directory is needed as the database is stored there
        # but is not created automatically
        os.makedirs(app.instance_path)
    except OSError:
        # print(f"Error: Could not create directory {app.instance_path}")
        pass

    Markdown(app)
    blog_mgr.db.init_app(app)

    app.register_blueprint(blog_mgr.auth.bp)
    
    app.add_url_rule('/', endpoint='blog.index')
    app.register_blueprint(bp)

    return app
