"""
Module to define Celery instance
Tutorial:
https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html
"""
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "opennews.settings.dev")

app = Celery("opennews")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")


# Load task modules from all registered Django apps.
app.autodiscover_tasks()

from celery import current_app

# `after_task_publish` is available in celery 3.1+
# for older versions use the deprecated `task_sent` signal
from celery.signals import after_task_publish

# when using celery versions older than 4.0, use body instead of headers


@after_task_publish.connect
def update_sent_state(sender=None, headers=None, body=None, **kwargs):
    """
    Use after task publish signal to change the task default state.
    By default, celery uses the state 'PENDING' for both pending and unknown
    tasks. We want to distinguish from unknown and pending tasks. As such, we set
    the default state to 'WAITING'. Any task that has 'PENDING' is unknown, and we can
    return a 404.
    """
    # the task may not exist if sent using `send_task` which
    # sends tasks by name, so fall back to the default result backend
    # if that is the case.

    # information about task are located in headers for task messages
    # using the task protocol version 2.
    info = headers if "task" in headers else body

    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend
    # Change status of task to 'WAITING'
    backend.store_result(info["id"], None, "WAITING")
