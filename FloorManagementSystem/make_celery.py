
"""
Create the Celery application instance.

:param flask_app: The Flask application instance.
:type flask_app: flask.Flask
:return: The Celery application instance.
:rtype: celery.Celery
"""

from task_app import create_app

"""
Create the Celery application instance.

:param flask_app: The Flask application instance.
:type flask_app: flask.Flask
:return: The Celery application instance.
:rtype: celery.Celery
"""
flask_app = create_app()
celery_app = flask_app.extensions["celery"]
