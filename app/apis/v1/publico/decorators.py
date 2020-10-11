from functools import wraps
from flask import request

from app.core.common.helpers import (
    to_list,
)
from app.core.common.custom_exceptions import RequestError
from .models.publico_news import PublicoNews


from app.core.common.decorators import _base_prevent_duplicate_jobs
from .publico_router import publico_queue


def prevent_duplicate_publico_jobs(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        _base_prevent_duplicate_jobs(publico_queue)
        return f(*args, **kwargs)

    return decorated


def validate_urls(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = to_list(request.get_json().get("url"))
        if len(data) > 50:
            raise RequestError("Too many URLS to search. Please provide up to 50 URLS!")

        valid_url = [PublicoNews.validate_url(url) for url in data]
        invalid_urls_index = [i for i, value in enumerate(valid_url) if not value]
        if len(invalid_urls_index) != 0:
            raise RequestError(
                f"Invalid URLs provided at position: {invalid_urls_index}"
            )
        return f(*args, **kwargs)

    return decorated
