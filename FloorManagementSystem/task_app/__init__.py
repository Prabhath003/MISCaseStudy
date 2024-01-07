"""
This file creates a flask application with celery and flask-sqlalchemy as dependencies.
It also sets up authentication using flask-login.

The functions and methods are well documented using Python Docstrings.
"""
from celery import Celery
from celery import Task
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app() -> Flask:
    """
    This function creates a flask application with the given configuration.
    The configuration is loaded from the environment variables and includes:
    - SECRET_KEY
    - SQLALCHEMY_DATABASE_URI
    - CELERY configuration

    The application also initializes the database and registers the blueprints.

    Returns:
        Flask: The created flask application.
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)

    from . import views
    from . import auth

    app.register_blueprint(views.bp, url_prefix="/")
    app.register_blueprint(auth.auth, url_prefix='/')

    from .models import User
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def celery_init_app(app: Flask) -> Celery:
    """
    This function initializes celery with the given flask application.
    It creates a custom celery task that can run in the flask application context.

    Args:
        app (Flask): The flask application.

    Returns:
        Celery: The initialized celery application.
    """
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app