import os

import redis
from rq import Worker, Queue, Connection

listen = ["publico", "cm"]

redis_url = os.getenv("REDISTOGO_URL", "redis://localhost:6379")

# If no redis URL in system env, setup a fake redis server
conn = redis.from_url(redis_url)

if __name__ == "__main__":
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
