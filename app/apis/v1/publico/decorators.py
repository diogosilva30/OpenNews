from functools import wraps
from flask import request
import json

from app.core.common.helpers import to_list, date_from_string, number_of_months_between_2_dates
from app.core.common.custom_exceptions import RequestError
from .models.publico_news import PublicoNews


def validate_urls(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = to_list(request.get_json().get("url"))
        if len(data) > 50:
            raise RequestError(
                'Too many URLS to search. Please provide up to 50 URLS!')
        for url in data:
            PublicoNews.validate_url(url)
        return f(*args, **kwargs)
    return decorated


def validate_dates(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            json_doc = request.get_json()
            start_date = date_from_string(json_doc.get("start_date"))
            end_date = date_from_string(json_doc.get("end_date"))
            months_diff = number_of_months_between_2_dates(
                start_date, end_date)
            if months_diff < 0:
                raise RequestError(
                    'Invalid dates provided! Starting date cannot be greater than end date.')
            if months_diff > 3:
                raise RequestError(
                    'Date range is too big. Please limit your search up to 3 months.')
        except ValueError:
            raise RequestError(
                'Invalid date string format provided! Please provide dates in the following format: dd/mm/AAAA')

        return f(*args, **kwargs)
    return decorated
