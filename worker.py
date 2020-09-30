import os

from fakeredis import FakeStrictRedis
import redis
from rq import Worker, Queue, Connection

listen = ['default']

redis_url = os.getenv('REDISTOGO_URL', None)

# If no redis URL in system env, setup a fake redis server
conn = redis.from_url(
    redis_url) if redis_url is not None else FakeStrictRedis()

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
