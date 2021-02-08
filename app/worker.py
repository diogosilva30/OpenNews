"""
Worker file
"""
import django_rq

worker = django_rq.get_worker()  # Returns a worker for "default" queue
worker.work()
