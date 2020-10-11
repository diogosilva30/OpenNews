from .cm_router import api as cm_api

# Create CM queue
from rq import Queue
from worker import conn

cm_queue = Queue(connection=conn)
