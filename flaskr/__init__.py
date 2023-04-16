import os
from flask import Flask

# application factory function
def create_app(test_config=None):
    # create and configure the app instance. __name__ is the name of the current
    # python module. It tells the app where it is located so it can make paths.
    # instance_relative_config=True tells the app that the config files are relative
    # to the instance folder. The instance folder is located outside the flaskr package
    # and can hold data that should not be committed to version control such as config
    # secrets and the database.
    app = Flask(__name__, instance_relative_config=True)
    # this sets some default config that the app uses:
    # SECRET_KEY is used by Flask and extensions to keep data safe. It's set to 'dev'
    # to provide a convenient value during development, but it should be set to a
    # random value when deploying.
    # DATABASE is the path where the SQLite database file will be saved. It's under
    # app.instance_path which is the path that Flask has chosen for the instance folder.
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config if it exists, when not testing

        # this overrides the default config with values taken from the config.py
        # file in the instance folder if it exists. This can be used to set things
        # like a proper SECRET_KEY when deploying.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config

        # test_config can also be passed in and will be used instead of instance config.
        # this is os the tests we write can be configured independently of any development
        # values.
        app.config.from_mapping(test_config)

    # check instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'hello world'
    
    from . import db
    db.init_app(app)

    # import and register the blueprint from the factory using
    # app.register_blueprint(). place the new code at the end of the factory
    # function before returning the app

    from . import auth
    app.register_blueprint(auth.bp)

    # import and register the blueprint from the factory using app.register_blueprint()
    # place the new code at the end of the factory before reutrning the app

    # unlike with the auth blueprint, the blog blueprint does not have a url prefix,
    # so the index view will be at /, the create view will be at at /create, etc.
    # The blog is a main feature so we use it as the main index page.

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')


    return app