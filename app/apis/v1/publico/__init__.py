from .publico_router import api as publico_api

# Create Publico queue
from rq import Queue
from worker import conn

cm_queue = Queue(connection=conn)
