from flask import Flask

from .config import config_by_name

from rq import Queue
from worker import conn

# Create CM queue
cm_queue = Queue(connection=conn)
# Create Publico queue
publico_queue = Queue(connection=conn)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.config["RESTX_MASK_SWAGGER"] = False
    app.config["JSON_SORT_KEYS"] = False
    app.config["ERROR_404_HELP"] = False
    return app
