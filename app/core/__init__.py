from flask import Flask
from rq import Queue
from worker import conn
from .config import config_by_name


# Create CM queue
cm_queue = Queue("cm", connection=conn)
# Create Publico queue
publico_queue = Queue("publico", connection=conn)


def create_app(config_name):
    """ Creates and returns an Flask app instance"""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.config["RESTX_MASK_SWAGGER"] = False
    app.config["JSON_SORT_KEYS"] = False
    app.config["ERROR_404_HELP"] = False
    return app
