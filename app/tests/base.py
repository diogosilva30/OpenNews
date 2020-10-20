""" This modules provides the base setup for the tests"""
from flask_testing import TestCase
from redislite import Redis
from rq import Queue

from manage import app
from app.apis.v1.results.results_service import get_results

# Start fake redis server
fake_redis_server = Redis("RQ.rdb")
# Start fake redis queue
fake_publico_queue = Queue(name="publico", is_async=False, connection=fake_redis_server)
fake_cm_queue = Queue(name="cm", is_async=False, connection=fake_redis_server)


def get_results_from_fake_queue(job_id):
    """ Gets the job results from a fake queue"""
    return get_results(job_id, fake_redis_server)


class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        app.config.from_object("app.core.config.TestingConfig")
        return app

    def setUp(self):
        pass

    def tearDown(self):
        pass
