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
app.conf.update(
    task_serializer="pickle",
    result_serializer="pickle",
    accept_content=["json"],
)
# Load task modules from all registered Django apps.
app.autodiscover_tasks()

from celery import current_app

# `after_task_publish` is available in celery 3.1+
# for older versions use the deprecated `task_sent` signal
from celery.signals import after_task_publish


@after_task_publish.connect
def task_sent_handler(sender=None, headers=None, body=None, **kwargs):
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    info = headers if "task" in headers else body

    from celery.result import AsyncResult

    task = AsyncResult(info["id"])
    task.update_state(state="SENT")
    print(sender, task)
    print(task.state)
    print(
        "after_task_publish for task id {info[id]}".format(
            info=info,
        )
    )
