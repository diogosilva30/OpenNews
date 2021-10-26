from api.opennews.settings.dev import DEBUG
from .base import *

# Execute celery tasks in synchronous mode
CELERY_TASK_ALWAYS_EAGER = True

DEBUG = True
