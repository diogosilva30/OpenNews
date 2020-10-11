from functools import wraps
from app.core.common.decorators import _base_prevent_duplicate_jobs
from app.apis.v1.cm import cm_queue


def prevent_duplicate_cm_jobs(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        _base_prevent_duplicate_jobs(cm_queue)
        return f(*args, **kwargs)

    return decorated
